## 18.0.1.0.0 (2026-05-16)

- Migration to 18.0.
- Drop dependency on `account_receipt_base` (not migrated to 18.0).
- Reintroduce the partner-level toggle as
  `res.partner.use_sale_receipts`; OpenUpgrade pre-migration renames the
  legacy `res_partner.use_receipts` column.
- Add a `receipts` checkbox on the `sale.advance.payment.inv` wizard,
  defaulted from the sale order's flag and authoritative for the wizard
  run.

## 14.0

This module comes from modules `l10n_it_corrispettivi` and
`l10n_it_corrispettivi_sale` of <https://github.com/OCA/l10n-italy>
version 12.
