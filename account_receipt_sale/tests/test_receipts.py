# Copyright 2018 Simone Rubino
# Copyright 2022 Lorenzo Battistini
# Copyright 2023 Simone Rubino - TAKOBI
# Copyright 2026 Francesco Ballerini
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import tagged

from odoo.addons.sale.tests.common import TestSaleCommon


@tagged("post_install", "-at_install")
class TestReceiptsSale(TestSaleCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.out_receipt_journal = cls.env["account.journal"].create(
            {
                "name": "Sale Receipts Journal",
                "code": "SREC",
                "type": "sale",
                "receipts": True,
                "sequence": 99,
            }
        )
        cls.receipt_partner = cls.env["res.partner"].create(
            {"name": "Receipt partner", "use_sale_receipts": True}
        )
        cls.no_receipt_partner = cls.env["res.partner"].create(
            {"name": "No receipt partner", "use_sale_receipts": False}
        )
        cls.product = cls.env["product.product"].create(
            {"name": "Test product", "list_price": 100.0, "taxes_id": False}
        )

    def _create_order(self, partner):
        return self.env["sale.order"].create(
            {
                "partner_id": partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 1.0,
                            "price_unit": 100.0,
                        },
                    )
                ],
            }
        )

    def _open_wizard(self, orders, **values):
        wizard = (
            self.env["sale.advance.payment.inv"]
            .with_context(active_ids=orders.ids, active_model="sale.order")
            .create(values)
        )
        return wizard

    def test_order_partner_default(self):
        order_receipts = self._create_order(self.receipt_partner)
        self.assertTrue(order_receipts.receipts)
        order_no_receipts = self._create_order(self.no_receipt_partner)
        self.assertFalse(order_no_receipts.receipts)
        order_no_receipts.partner_id = self.receipt_partner
        self.assertTrue(order_no_receipts.receipts)

    def test_wizard_default_from_order(self):
        order = self._create_order(self.receipt_partner)
        wizard = self._open_wizard(order)
        self.assertTrue(wizard.receipts)
        order_no = self._create_order(self.no_receipt_partner)
        wizard_no = self._open_wizard(order_no)
        self.assertFalse(wizard_no.receipts)

    def test_create_receipt_delivered(self):
        order = self._create_order(self.receipt_partner)
        order.action_confirm()
        order.order_line.qty_delivered = 1.0
        wizard = self._open_wizard(order, advance_payment_method="delivered")
        wizard.create_invoices()
        receipt = order.receipt_ids
        self.assertEqual(len(receipt), 1)
        self.assertEqual(receipt.move_type, "out_receipt")
        self.assertTrue(receipt.journal_id.receipts)

    def test_wizard_overrides_order_flag(self):
        order = self._create_order(self.receipt_partner)
        order.action_confirm()
        order.order_line.qty_delivered = 1.0
        wizard = self._open_wizard(
            order, advance_payment_method="delivered", receipts=False
        )
        wizard.create_invoices()
        self.assertEqual(len(order.invoice_ids), 1)
        self.assertEqual(order.invoice_ids.move_type, "out_invoice")
        self.assertFalse(order.receipt_ids)

    def test_wizard_forces_receipt_on_invoice_order(self):
        order = self._create_order(self.no_receipt_partner)
        order.action_confirm()
        order.order_line.qty_delivered = 1.0
        wizard = self._open_wizard(
            order, advance_payment_method="delivered", receipts=True
        )
        wizard.create_invoices()
        self.assertEqual(len(order.receipt_ids), 1)
        self.assertEqual(order.receipt_ids.move_type, "out_receipt")

    def test_create_receipt_down_payment(self):
        order = self._create_order(self.receipt_partner)
        order.action_confirm()
        wizard = self._open_wizard(
            order,
            advance_payment_method="percentage",
            amount=50.0,
        )
        wizard.create_invoices()
        self.assertEqual(len(order.receipt_ids), 1)
        self.assertEqual(order.receipt_ids.move_type, "out_receipt")

    def test_qty_and_amount_invoiced_rollup(self):
        order = self._create_order(self.receipt_partner)
        order.action_confirm()
        order.order_line.qty_delivered = 1.0
        wizard = self._open_wizard(order, advance_payment_method="delivered")
        wizard.create_invoices()
        receipt = order.receipt_ids
        receipt.action_post()
        self.assertEqual(order.order_line.qty_invoiced, 1.0)
        self.assertEqual(order.order_line.untaxed_amount_invoiced, 100.0)
