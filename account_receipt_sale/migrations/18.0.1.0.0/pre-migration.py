# Copyright 2026 Francesco Ballerini
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    if openupgrade.column_exists(
        env.cr, "res_partner", "use_receipts"
    ) and not openupgrade.column_exists(env.cr, "res_partner", "use_sale_receipts"):
        openupgrade.rename_columns(
            env.cr,
            {"res_partner": [("use_receipts", "use_sale_receipts")]},
        )
