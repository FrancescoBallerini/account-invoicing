from odoo import api, fields, models


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    receipts = fields.Boolean()

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if "receipts" in fields_list:
            orders = self.env["sale.order"].browse(
                self.env.context.get("active_ids", [])
            )
            if orders:
                res["receipts"] = all(orders.mapped("receipts"))
        return res

    def _prepare_invoice_values(self, order, so_lines, accounts):
        invoice_vals = super()._prepare_invoice_values(order, so_lines, accounts)
        if self.receipts:
            invoice_vals["move_type"] = "out_receipt"
        return invoice_vals

    def _create_invoices(self, sale_orders):
        return super(
            SaleAdvancePaymentInv,
            self.with_context(force_receipts=self.receipts),
        )._create_invoices(sale_orders)

    def create_invoices(self):
        action = super().create_invoices()
        if self.receipts:
            return self.sale_order_ids.action_view_receipt()
        return action
