# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError




class MovingForm(models.Model):
    _name = 'moving.form'
    _rec_name = 'order_number'

    order_number = fields.Char(string="التسلسل", readonly=True)
    name = fields.Char(string="الاسم")
    fleet_vehicle_id = fields.Many2one('fleet.vehicle',string="المركبة", readonly=True)
    driver_id = fields.Many2one('res.partner',string="السائق", readonly=True)
    journal_id = fields.Many2one('account.journal',string="اليومية", readonly=True)
    from_addrress = fields.Char(string="مكان الانطلاق" )
    to_addrress = fields.Char(string="مكان الهدف",)
    date = fields.Date(string="تاريخ التحرير",required=False)
    from_date = fields.Date(string="من تاريخ",required=False)
    to_date = fields.Date(string="الى تاريخ",required=False)
    note = fields.Text(string="ملاحظات",)
    amount_company = fields.Float(string="المبلغ",required=False)
    state = fields.Selection([('draft', 'مسودة'), ('closed', 'مغلق')], default='draft', required=True, tracking=True, copy=False)
    account_move_id = fields.Many2one('account.move',string="القيد",readonly=True)
    try_vehicle_id = fields.Many2one('try.vehicle',string="try_vehicle_id",invisible=True)


    type = fields.Selection([('expense', 'مصروف'), ('revenues', 'ايرادات')],string="النوع", required=False, copy=False)

    @api.model
    def create(self, vals):
        if 'order_number' not in vals:
            vals['order_number'] = self.env['ir.sequence'].next_by_code('moving.form')
        return super(MovingForm, self).create(vals)

    def open_this(self):
        self.account_move_id.button_draft()
        line_ids = self.account_move_id.line_ids.ids
        lines = self.env['account.move.line'].search([('move_id', '=', self.account_move_id.id)])
        lines.unlink()
        self.state = "draft"

    def close_this(self):
        if not self.journal_id:
            raise UserError(_('يجب تعبئة حقل اليومية') )
        if self.type == "expense":
            if not self.fleet_vehicle_id.account_expense:
                raise UserError(_('يجب تعبئة حقل حساب المصاريف بالمركبة'))
            account_id = self.fleet_vehicle_id.account_expense
        elif self.type == "revenues":
            if not self.fleet_vehicle_id.account_revenues:
                raise UserError(_('يجب تعبئة حقل حساب الايرادات بالمركبة'))
            account_id = self.fleet_vehicle_id.account_revenues

        if not self.account_move_id:
            move_line_vals = []
            if self.type == "expense":
                line1 = (0, 0, {'name': self.name,'debit': 0,'credit': self.amount_company,'account_id': self.journal_id.default_debit_account_id.id,'partner_id': self.driver_id.id})
                line2 = (0, 0, {'name': self.name,'debit': self.amount_company,'credit': 0,'account_id': account_id.id,'partner_id': self.driver_id.id})
            elif self.type == "revenues":
                line1 = (0, 0, {'name': self.name,'debit': self.amount_company,'credit': 0,'account_id': self.journal_id.default_debit_account_id.id,'partner_id': self.driver_id.id})
                line2 = (0, 0, {'name': self.name,'debit': 0,'credit': self.amount_company,'account_id': account_id.id,'partner_id': self.driver_id.id})
            move_line_vals.append(line1)
            move_line_vals.append(line2)
            move_vals = {
                "date": self.date,
                "journal_id": self.journal_id.id,
                "line_ids": move_line_vals,
            }
            new_move_id = self.env['account.move'].create(move_vals)
            new_move_id.post()
            self.account_move_id = new_move_id.id
        else:
            self.account_move_id.button_draft()
            move_line_vals = []
            if self.type == "expense":
                line1 = (0, 0, {'name': self.name,'debit': 0,'credit': self.amount_company,'account_id': self.journal_id.default_debit_account_id.id,'partner_id': self.driver_id.id})
                line2 = (0, 0, {'name': self.name,'debit': self.amount_company,'credit': 0,'account_id': account_id.id,'partner_id': self.driver_id.id})
            elif self.type == "revenues":
                line1 = (0, 0, {'name': self.name,'debit': self.amount_company,'credit': 0,'account_id': self.journal_id.default_debit_account_id.id,'partner_id': self.driver_id.id})
                line2 = (0, 0, {'name': self.name,'debit': 0,'credit': self.amount_company,'account_id': account_id.id,'partner_id': self.driver_id.id})

            # line1 = (0, 0, {'name': self.name,'debit': self.amount_company,'credit': 0,'account_id': self.journal_id.default_debit_account_id.id,'partner_id': self.driver_id.id})
            # line2 = (0, 0, {'name': self.name,'debit': 0,'credit': self.amount_company,'account_id': account_id.id,'partner_id': self.driver_id.id})
            move_line_vals.append(line1)
            move_line_vals.append(line2)
            self.account_move_id.line_ids = move_line_vals
            self.account_move_id.post()

        self.state = "closed"



