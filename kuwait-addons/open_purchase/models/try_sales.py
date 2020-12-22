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
    try_vehicle_ids = fields.One2many('try.vehicle', 'try_sales_id', string="TRY VEHICLE")
    state = fields.Selection([('draft', 'مسودة'), ('sumation', 'محتسب')], default='draft', tracking=True,copy=False)
    date = fields.Date(string="التاريخ")
    month = fields.Selection([('1','1'),('2','2'),('3','3'),('4','4'),('5','5'),('6','6'),('7','7'),('8','8'),('9','9'),('10','10'),('11','11'),('12','12')],string="الشهر")
    note = fields.Char(string="ملاحظات")

    @api.model
    def create(self, vals):
        if 'order_number' not in vals:
            vals['order_number'] = self.env['ir.sequence'].next_by_code('try.sales')
        return super(TrySales, self).create(vals)

    def sumation_function(self):
        open_purchase_ids = self.env['open.purchase'].search([('try_sales_id', '=', False),('state', '=', 'closed')])
        for o in open_purchase_ids:
            o.try_sales_id = self.id
        try_vehicle_ids = self.env['try.vehicle'].search([('try_sales_id', '=', False),('state', '=', 'sumation')])
        for o in try_vehicle_ids:
            o.try_sales_id = self.id
        hr_expense_ids = self.env['hr.expense'].search([('try_sales_id', '=', False),('type_in_not', '=', "not")])
        for h in hr_expense_ids:
            h.try_sales_id = self.id
        self.state = "sumation"

    def cancel_sumation_function(self):
        open_purchase_ids = self.env['open.purchase'].search([('try_sales_id', '=', self.id)])
        for o in open_purchase_ids:
            o.try_sales_id = False
        try_vehicle_ids = self.env['try.vehicle'].search([('try_sales_id', '=', self.id)])
        for o in try_vehicle_ids:
            o.try_sales_id = False
        hr_expense_ids = self.env['hr.expense'].search([('try_sales_id', '=', self.id)])
        for h in hr_expense_ids:
            h.try_sales_id = False
        self.state = "draft"
