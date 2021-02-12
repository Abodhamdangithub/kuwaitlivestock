# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class HrExpense(models.Model):
    _inherit = 'hr.expense'


    try_sales_id = fields.Many2one('try.sales',string="try.sales", invisible=True)
    type_in_not = fields.Selection([('in', 'برجعة'), ('not', 'بدون رجعة')], required=True, tracking=True,copy=False,string="برجعة/بدون رجعه")


    def cancel_expensetwo(self):
        print ("self.state1",self.state)
        self.state = 'refused'
        print ("self.state",self.state)
        self.sheet_id.state = 'cancel'
        self.sheet_id.account_move_id.type_expenses_purchase = 'normal'
        self.sheet_id.account_move_id.button_draft()
        self.sheet_id.account_move_id.line_ids.unlink()
        self.sheet_id.account_move_id.state = 'cancel'
        self.sheet_id.payment_id_id.action_draft()
        self.sheet_id.payment_id_id.cancel()