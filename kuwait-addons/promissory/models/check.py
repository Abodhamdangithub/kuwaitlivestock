# -*- coding: utf-8 -*-
import time
from odoo import api, models, fields
from datetime import datetime
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
import requests
from datetime import datetime, date, time
from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
from odoo.tools import float_is_zero, float_compare, safe_eval, date_utils, email_split, email_escape_char, email_re
from odoo.tools.misc import formatLang, format_date, get_lang

from datetime import date, timedelta
from itertools import groupby
from itertools import zip_longest
from hashlib import sha256
from json import dumps

import json
import re

class check(models.Model):
    _name = 'check'

    name_partner_id = fields.Many2one('res.partner', string='العميل')
    amount = fields.Float(string="القيمة", required=True,readonly=True, states={'draft': [('readonly', False)]})
    edit_date = fields.Date(string="تاريخ التحرير", required=True, default=datetime.today(),readonly=True, states={'draft': [('readonly', False)]})
    get_date = fields.Date(string="تاريخ الاستحقاق", required=True, default=datetime.today(),readonly=True, states={'draft': [('readonly', False)]})
    state = fields.Selection([('draft', 'مسوده'), ('sndook', 'الصندوق'), ('in_street', 'في الطريق'), ('bank','بنك'), ('cancel', 'ملغي')], string='الحاله', default='draft',readonly=True, states={'draft': [('readonly', False)]})
    source_payment_id = fields.Many2one('account.payment', 'Source payment', readonly=True, states={'draft': [('readonly', False)]})
    journal_id = fields.Many2one('account.journal', string="اليوميه")
    name = fields.Char(string="رقم الشيك")


    def return_movelines(self,type):
        all_move_vals = []
        for check in self:
            if type == "to":
                now = datetime.now()
                move_vals = {
                    'date': now,
                    'ref': check.name,
                    'journal_id': check.journal_id.id,
                    'partner_id': check.name_partner_id.id,
                    'line_ids': [
                        # Receivable / Payable / Transfer line.
                        (0, 0, {
                            'name': check.name,
                            'amount_currency':  0.0,
                            'debit': check.amount,
                            'credit': 0.0,
                            'account_id': check.journal_id.default_debit_account_id.id,
                        }),
                        # Liquidity line.
                        (0, 0, {
                            'name': check.name,
                            'amount_currency': 0.0,
                            'debit':  0.0,
                            'credit': check.amount ,
                            'account_id': check.journal_id.default_credit_account_id.id,
                        }),
                    ],
                }
            else:
                now = datetime.now()
                move_vals = {
                    'date': now,
                    'ref': check.name,
                    'journal_id': check.journal_id.id,
                    'partner_id': check.name_partner_id.id,
                    'line_ids': [
                        (0, 0, {
                            'name': check.name,
                            'amount_currency':  0.0,
                            'debit': 0.0,
                            'credit': check.amount,
                            'account_id': check.journal_id.default_debit_account_id.id,
                        }),
                        # Liquidity line.
                        (0, 0, {
                            'name': check.name,
                            'amount_currency': 0.0,
                            'debit':  check.amount,
                            'credit': 0.0 ,
                            'account_id': check.journal_id.default_credit_account_id.id,
                        }),
                    ],
                }


            all_move_vals.append(move_vals)
        return all_move_vals

    def to_street(self):
        AccountMove = self.env['account.move'].with_context(default_type='entry')
        for rec in self:
            moves = AccountMove.create(rec.return_movelines("to"))
            moves.filtered(lambda move: move.journal_id.post_at != 'bank_rec').post()
            if rec.state == "sndook":
                rec.state = 'in_street'
            elif rec.state == "in_street":
                rec.state = 'bank'


        return True

    def back_street(self):
        AccountMove = self.env['account.move'].with_context(default_type='entry')
        for rec in self:
            moves = AccountMove.create(rec.return_movelines("back"))
            moves.filtered(lambda move: move.journal_id.post_at != 'bank_rec').post()
            if rec.state == "bank":
                rec.state = 'in_street'
            elif rec.state == "in_street":
                rec.state = 'sndook'


        return True



