# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
from odoo.exceptions import UserError, ValidationError


class AccountBankGet(models.Model):
    _name = 'account.bank.get'

    account_payment_ids = fields.Many2many('account.payment',readonly=False,string="account.payment")


    def ok_function(self):
        account_add_custody_obj = self.env['account.add.custody']
        account_add_custody_active= self.env['account.add.custody'].browse(self.env.context['active_id'])
        for line in self.account_payment_ids:
            res = account_add_custody_obj.create( {
                'name': line.name,
                'amount': line.amount,
                'account_id': line.journal_id.default_debit_account_id.id,
                'account_payment_id': line.id,
                })
            res.account_bank_import_id = account_add_custody_active.id
            line.account_add_custody_ids = res.id
        return True


