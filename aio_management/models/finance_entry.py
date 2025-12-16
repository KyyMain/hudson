from odoo import api, fields, models


class PoolFinanceEntry(models.Model):
    _name = "hudson.pool.finance.entry"
    _description = "Catatan Keuangan Divisi Kolam"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Keterangan", required=True, tracking=True)
    entry_type = fields.Selection(
        [("income", "Uang Masuk"), ("expense", "Uang Keluar")],
        string="Tipe",
        required=True,
        default="income",
        tracking=True,
    )
    amount = fields.Float(string="Nominal", required=True)
    date = fields.Date(default=fields.Date.context_today, string="Tanggal", tracking=True)
    pool_id = fields.Many2one("hudson.pool", string="Kolam")
    customer_id = fields.Many2one("hudson.pool.customer", string="Pelanggan")
    notes = fields.Text(string="Catatan")
    signed_amount = fields.Float(compute="_compute_signed_amount", string="Nominal (+/-)", store=False)

    @api.depends("amount", "entry_type")
    def _compute_signed_amount(self):
        for record in self:
            sign = 1 if record.entry_type == "income" else -1
            record.signed_amount = (record.amount or 0.0) * sign

    def action_view_related_pool(self):
        self.ensure_one()
        if not self.pool_id:
            return False
        return {
            "type": "ir.actions.act_window",
            "name": "Kolam",
            "res_model": "hudson.pool",
            "view_mode": "form",
            "res_id": self.pool_id.id,
        }
