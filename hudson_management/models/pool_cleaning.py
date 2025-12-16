from odoo import api, fields, models


class PoolCleaningType(models.Model):
    _name = "hudson.pool.cleaning.type"
    _description = "Jenis Pembersihan Kolam"

    name = fields.Char(required=True)
    code = fields.Char(string="Kode")
    description = fields.Text(string="Deskripsi")
    level = fields.Selection(
        [
            ("economy", "Ekonomi"),
            ("business", "Bisnis"),
            ("exclusive", "Eksklusif"),
        ],
        string="Kategori",
        required=True,
    )
    base_price = fields.Float(string="Harga Dasar")


class Pool(models.Model):
    _name = "hudson.pool"
    _description = "Data Kolam"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Nama Kolam", required=True, tracking=True)
    customer_id = fields.Many2one("hudson.pool.customer", string="Pelanggan", required=True, ondelete="cascade")
    cleaning_type_id = fields.Many2one("hudson.pool.cleaning.type", string="Jenis Pembersihan", tracking=True)
    size_m2 = fields.Float(string="Luas (m2)")
    length = fields.Float(string="Panjang (m)")
    width = fields.Float(string="Lebar (m)")
    depth = fields.Float(string="Kedalaman (m)")
    water_type = fields.Selection(
        [("salt", "Air Garam"), ("fresh", "Air Tawar"), ("chlorine", "Klorin")],
        string="Jenis Air",
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("scheduled", "Terjadwal"),
            ("in_progress", "Sedang Dibersihkan"),
            ("cleaned", "Selesai"),
            ("delayed", "Tertunda"),
        ],
        default="draft",
        tracking=True,
    )
    next_cleaning_date = fields.Date(string="Jadwal Berikutnya")
    notes = fields.Text(string="Catatan")
    cleaning_job_ids = fields.One2many("hudson.pool.cleaning.job", "pool_id", string="Riwayat Pembersihan")
    cleaning_job_count = fields.Integer(compute="_compute_cleaning_job_count")

    @api.depends("cleaning_job_ids")
    def _compute_cleaning_job_count(self):
        for record in self:
            record.cleaning_job_count = len(record.cleaning_job_ids)

    def action_open_cleaning_jobs(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Pembersihan Kolam",
            "res_model": "hudson.pool.cleaning.job",
            "view_mode": "tree,form",
            "domain": [("pool_id", "=", self.id)],
            "context": {
                "default_pool_id": self.id,
                "default_customer_id": self.customer_id.id,
                "default_cleaning_type_id": self.cleaning_type_id.id,
            },
        }


class PoolCleaningJob(models.Model):
    _name = "hudson.pool.cleaning.job"
    _description = "Aktivitas Pembersihan Kolam"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Nama Tugas", required=True, tracking=True)
    pool_id = fields.Many2one("hudson.pool", string="Kolam", required=True, ondelete="cascade")
    customer_id = fields.Many2one("hudson.pool.customer", string="Pelanggan", related="pool_id.customer_id", store=True)
    cleaning_type_id = fields.Many2one("hudson.pool.cleaning.type", string="Jenis Pembersihan", required=True)
    scheduled_date = fields.Datetime(string="Dijadwalkan", tracking=True)
    completed_date = fields.Datetime(string="Selesai")
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("scheduled", "Terjadwal"),
            ("in_progress", "Sedang Dibersihkan"),
            ("cleaned", "Selesai"),
            ("delayed", "Tertunda"),
        ],
        default="draft",
        tracking=True,
    )
    reason_delay = fields.Char(string="Alasan Penundaan")
    notes = fields.Text(string="Catatan")

    def action_set_state(self, target_state):
        for record in self:
            record.state = target_state
        return True

    def action_mark_cleaned(self):
        return self.action_set_state("cleaned")

    def action_mark_in_progress(self):
        return self.action_set_state("in_progress")

    def action_mark_delayed(self):
        return self.action_set_state("delayed")
