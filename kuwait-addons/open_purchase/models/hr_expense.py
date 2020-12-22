# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class HrExpense(models.Model):
    _inherit = 'hr.expense'


    try_sales_id = fields.Many2one('try.sales',string="try.sales", invisible=True)
    type_in_not = fields.Selection([('in', 'برجعة'), ('not', 'بدون رجعة')], required=True, tracking=True,copy=False,string="برجعة/بدون رجعه")
