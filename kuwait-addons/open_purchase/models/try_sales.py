# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime


class TrySales(models.Model):
    _name = 'try.sales'
    _rec_name = 'order_number'

    order_number = fields.Char(string="التسلسل", readonly=True)
    open_purchase_ids = fields.One2many('open.purchase', 'try_sales_id', string="open purchase")
    hr_expense_ids = fields.One2many('hr.expense', 'try_sales_id', string="hr expense")
    state = fields.Selection([('draft', 'مسودة'), ('sumation', 'محتسب')], default='draft', tracking=True,copy=False)
    from_date = fields.Date(string="من تاريخ")
    to_date = fields.Date(string="الى تاريخ")


    @api.model
    def create(self, vals):
        if 'order_number' not in vals:
            vals['order_number'] = self.env['ir.sequence'].next_by_code('try.sales')
        return super(TrySales, self).create(vals)

    def sumation_function(self):
        open_purchase_ids = self.env['open.purchase'].search([('try_sales_id', '=', False),('state', '=', 'closed'),('date_close', '>=', self.from_date),('date_close', '<=', self.to_date)])
        for o in open_purchase_ids:
            o.try_sales_id = self.id

        hr_expense_ids = self.env['hr.expense'].search([('try_sales_id', '=', False),('date', '>=', self.from_date),('date', '<=', self.to_date)])
        for h in hr_expense_ids:
            h.try_sales_id = self.id
        self.state = "sumation"

    def cancel_sumation_function(self):
        open_purchase_ids = self.env['open.purchase'].search([('try_sales_id', '=', self.id)])
        for o in open_purchase_ids:
            o.try_sales_id = False

        hr_expense_ids = self.env['hr.expense'].search([('try_sales_id', '=', self.id)])
        for h in hr_expense_ids:
            h.try_sales_id = False
        self.state = "draft"
