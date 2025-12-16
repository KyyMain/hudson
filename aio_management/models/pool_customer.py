from odoo import api, fields, models


class PoolCustomer(models.Model):
    _name = "hudson.pool.customer"
    _description = "Pelanggan Kolam"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Nama", required=True, tracking=True)
    phone = fields.Char(string="Telepon", tracking=True)
    email = fields.Char(string="Email", tracking=True)
    address = fields.Char(string="Alamat")
    pool_ids = fields.One2many("hudson.pool", "customer_id", string="Kolam")
    active = fields.Boolean(default=True)
    pool_count = fields.Integer(compute="_compute_pool_count", string="Jumlah Kolam")
    latest_cleaning_state = fields.Selection(
        [
            ("draft", "Draft"),
            ("scheduled", "Terjadwal"),
            ("in_progress", "Berjalan"),
            ("cleaned", "Selesai"),
            ("delayed", "Tertunda"),
        ],
        string="Status Pembersihan Terbaru",
        compute="_compute_latest_cleaning_state",
        store=False,
    )

    @api.depends("pool_ids")
    def _compute_pool_count(self):
        for record in self:
            record.pool_count = len(record.pool_ids)

    @api.depends("pool_ids.cleaning_job_ids.state")
    def _compute_latest_cleaning_state(self):
        for record in self:
            jobs = record.pool_ids.mapped("cleaning_job_ids").sorted("scheduled_date", reverse=True)
            record.latest_cleaning_state = jobs[:1].state if jobs else False

    def action_open_pools(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Kolam",
            "res_model": "hudson.pool",
            "view_mode": "tree,form",
            "domain": [("customer_id", "=", self.id)],
            "context": {"default_customer_id": self.id},
        }
