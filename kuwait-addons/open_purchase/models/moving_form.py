# -*- coding: utf-8 -*-

from odoo import api, fields, models, _




class MovingForm(models.Model):
    _name = 'moving.form'

    name = fields.Char(string="Name" )
    fleet_vehicle_id = fields.Many2one('fleet.vehicle',string="المركبة", readonly=True)
    driver_id = fields.Many2one('res.partner',string="السائق", readonly=True)
    journal_id = fields.Many2one('account.journal',string="اليومية", readonly=True)
    account_id = fields.Many2one('account.account',string="الحساب", readonly=True)
    from_addrress = fields.Char(string="مكان الانطلاق" )
    to_addrress = fields.Char(string="مكان الهدف",)
    date = fields.Date(string="تاريخ التحرير",)
    from_date = fields.Date(string="من تاريخ",)
    to_date = fields.Date(string="الى تاريخ",)
    note = fields.Text(string="ملاحظات",)
    amount_full = fields.Float(string="القيمة الكلية",)
    amount_company = fields.Float(string="قيمة الشركة",)
    amount_driver = fields.Float(string="قيمة السائق",)
    state = fields.Selection([('draft', 'مسودة'), ('closed', 'مغلق')], default='draft', required=True, tracking=True, copy=False)
    account_move_id = fields.Many2one('account.move',string="القيد",readonly=True)

    def open_this(self):
        self.account_move_id.button_draft()
        line_ids = self.account_move_id.line_ids.ids
        lines = self.env['account.move.line'].search([('move_id', '=', self.account_move_id.id)])
        lines.unlink()
        self.state = "draft"

    def close_this(self):
        if not self.account_move_id:
            move_line_vals = []
            line1 = (0, 0, {'name': self.name,'debit': self.amount_company,'credit': 0,'account_id': self.journal_id.default_debit_account_id.id,'partner_id': self.driver_id.id})
            line2 = (0, 0, {'name': self.name,'debit': 0,'credit': self.amount_company,'account_id': self.account_id.id,'partner_id': self.driver_id.id})
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
            line1 = (0, 0, {'name': self.name,'debit': self.amount_company,'credit': 0,'account_id': self.journal_id.default_debit_account_id.id,'partner_id': self.driver_id.id})
            line2 = (0, 0, {'name': self.name,'debit': 0,'credit': self.amount_company,'account_id': self.account_id.id,'partner_id': self.driver_id.id})
            move_line_vals.append(line1)
            move_line_vals.append(line2)
            self.account_move_id.line_ids = move_line_vals
            self.account_move_id.post()

        self.state = "closed"



