from odoo import api, fields, models


class PoolDashboard(models.Model):
    _name = "hudson.pool.dashboard"
    _description = "Dashboard Admin Kolam"
    _rec_name = "display_name"

    customer_count = fields.Integer(compute="_compute_metrics", string="Pelanggan")
    pool_count = fields.Integer(compute="_compute_metrics", string="Kolam")
    active_jobs = fields.Integer(compute="_compute_metrics", string="Tugas Aktif")
    income_total = fields.Float(compute="_compute_metrics", string="Uang Masuk")
    expense_total = fields.Float(compute="_compute_metrics", string="Uang Keluar")
    balance_total = fields.Float(compute="_compute_metrics", string="Saldo")

    @api.depends("customer_count")
    def _compute_metrics(self):
        customer_model = self.env["hudson.pool.customer"]
        pool_model = self.env["hudson.pool"]
        job_model = self.env["hudson.pool.cleaning.job"]
        finance_model = self.env["hudson.pool.finance.entry"]
        for record in self:
            record.customer_count = customer_model.search_count([])
            record.pool_count = pool_model.search_count([])
            record.active_jobs = job_model.search_count([("state", "in", ["scheduled", "in_progress"])] )
            income = sum(finance_model.search([("entry_type", "=", "income")]).mapped("amount"))
            expense = sum(finance_model.search([("entry_type", "=", "expense")]).mapped("amount"))
            record.income_total = income
            record.expense_total = expense
            record.balance_total = income - expense

    def _open_action(self, xml_id):
        return self.env.ref(xml_id).read()[0]

    def action_open_customers(self):
        return self._open_action("hudson_management.action_pool_customers")

    def action_open_pools(self):
        return self._open_action("hudson_management.action_pools")

    def action_open_cleaning_jobs(self):
        return self._open_action("hudson_management.action_pool_cleaning_jobs")

    def action_open_finance(self):
        return self._open_action("hudson_management.action_pool_finance_entries")

    def action_open_user_profile(self):
        user = self.env.user
        return {
            "type": "ir.actions.act_window",
            "res_model": "res.users",
            "view_mode": "form",
            "res_id": user.id,
            "target": "current",
        }
