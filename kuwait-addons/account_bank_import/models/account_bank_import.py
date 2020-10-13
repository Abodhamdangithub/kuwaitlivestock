# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
from odoo.exceptions import UserError, ValidationError

class AccountBankImport(models.Model):
    _name = 'account.bank.import'
    _rec_name = 'name'

    name = fields.Char(string="التسلسل",readonly=True,copy=False)
    date = fields.Date(string="التاريخ", default=datetime.today(),readonly=True,required=True)
    journal_id = fields.Many2one('account.journal',string="اليومية",required=True)
    employee_id = fields.Many2one('hr.employee',string="موظف الطريق")
    account_add_custody_ids = fields.One2many('account.add.custody','account_bank_import_id',string="السطور")
    state = fields.Selection( [('draft','مسوده'),('open','في الطريق'),('done','تم')],string="الحاله", default="draft",readonly=True)


    def _get_pay_view_form(self):
        self.ensure_one()
        data_obj = self.env['ir.model.data']
        return data_obj.get_object('account_bank_import', 'accountbankget_form')

    def accountbankget_action(self):
        view = self._get_pay_view_form()
        return {
            'name': _("Import bank"),
            'view_mode': 'form',
            'view_id': view.id,
            'view_type': 'form',
            'res_model': 'account.bank.get',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'domain': '[]',
            'context': {
            }
        }




    def go_draft(self):
        self.state = 'draft'

    def closed_done(self):
        for line_custody in self.account_add_custody_ids:
            AccountMove = line_custody.env['account.move'].with_context(default_type='entry')
            if not line_custody.move_id:
                moves = AccountMove.create(line_custody.return_movelines())
                moves.post()
                line_custody.move_id = moves.id
        self.state = 'done'

    def open_done(self):
        self.name = self.env['ir.sequence'].next_by_code('account.bank.import')
        self.state = 'open'




    def unlink(self):
        for me in self:
            raise UserError(_('لا يمكنك حذف %s '%(me.name)))
            super(AccountBankImport, me).unlink()



class AccountAddCustody(models.Model):
    _name = 'account.add.custody'
    _rec_name = 'name'

    name = fields.Char(string="الاسم", required=True)
    amount = fields.Float(string="قيمة ", required=True)
    account_id = fields.Many2one('account.account',string="الحساب", required=True)
    account_bank_import_id = fields.Many2one('account.bank.import',string="account.bank.import")
    move_id = fields.Many2one('account.move',string="القيد")
    account_payment_id = fields.Many2one('account.payment',string="account.payment")


    def unlink(self):
        for me in self:
            if me.move_id:
                raise UserError(_('لا يمكنك حذف %s '%(me.name)))
            me.account_payment_id.account_add_custody_ids = False
            super(AccountAddCustody, me).unlink()

    def return_movelines(self):
        all_move_vals = []
        for rec in self:

            move_vals = {
                'date': rec.account_bank_import_id.date,
                'ref': rec.account_bank_import_id.name,
                'journal_id': rec.account_bank_import_id.journal_id.id,
                'line_ids': [
                    (0, 0, {
                        'name': rec.name,
                        'debit': rec.amount,
                        'credit': 0.0,
                        'account_id': rec.account_bank_import_id.journal_id.default_credit_account_id.id,
                    }),
                    (0, 0, {
                        'name': rec.name,
                        'debit': 0.0,
                        'credit': rec.amount,
                        'account_id': rec.account_id.id,
                    }),
                ],
            }
            all_move_vals.append(move_vals)
            return all_move_vals

