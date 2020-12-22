# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime


class TryVehicle(models.Model):
    _name = 'try.vehicle'
    _rec_name = 'order_number'

    order_number = fields.Char(string="التسلسل", readonly=True)

    moving_form_ids = fields.Many2many('moving.form', 'relation_table_one', 'try_1', 'try_vehicle_id', string="الايرادات")
    hr_expense_ids = fields.Many2many('moving.form', 'relation_table_two', 'try_2', 'try_vehicle_id', string="المصاريف")
    vehicle_id = fields.Many2one('fleet.vehicle', string="السيارة",required=True)
    try_sales_id = fields.Many2one('try.sales',string="try.sales", invisible=True)
    state = fields.Selection([('draft', 'مسودة'), ('sumation', 'محتسب')], default='draft', tracking=True,copy=False)
    from_date = fields.Date(string="من تاريخ",required=True)
    to_date = fields.Date(string="الى تاريخ",required=True)
    date = fields.Date(string="التاريخ",required=True)
    note = fields.Char(string="ملاحظات",required=True)
    result = fields.Float(string="الصافي",readonly=True)
    commition = fields.Float(string="قيمة العمولة",readonly=True)
    result_last = fields.Float(string="الصافي بعد العمولة",readonly=True)
    @api.model
    def create(self, vals):
        if 'order_number' not in vals:
            vals['order_number'] = self.env['ir.sequence'].next_by_code('try.vehicle')
        return super(TryVehicle, self).create(vals)

    def sumation_function(self):
        moving_ids = self.env['moving.form'].search([('fleet_vehicle_id', '=', self.vehicle_id.id),('type', '=', "revenues"),('try_vehicle_id', '=', False),('state', '=', 'closed'),('date', '>=', self.from_date),('date', '<=', self.to_date)])
        self.moving_form_ids  = moving_ids.ids
        sum = 0.0
        for m in moving_ids:
            m.try_vehicle_id = self.id
            sum += m.amount_company

        expense_ids = self.env['moving.form'].search([('fleet_vehicle_id', '=', self.vehicle_id.id),('type', '=', "expense"),('try_vehicle_id', '=', False),('state', '=', 'closed'),('date', '>=', self.from_date),('date', '<=', self.to_date)])
        self.hr_expense_ids = expense_ids.ids
        for m in expense_ids:
            m.try_vehicle_id = self.id
            sum -= m.amount_company
        self.result = sum
        if self.result > 0:
            self.commition = sum*(self.vehicle_id.comm/100)
        else:
            self.commition = 0.0
        self.result_last = self.result - self.commition
        self.state = "sumation"

    def cancel_sumation_function(self):
        for o in self.moving_form_ids:
            o.try_vehicle_id = False
        for o in self.hr_expense_ids:
            o.try_vehicle_id = False
        self.result = 0.0
        self.commition = 0.0
        self.result_last = 0.0
        self.moving_form_ids = [(6,0, [])]
        self.hr_expense_ids = [(6,0, [])]
        self.state = "draft"
