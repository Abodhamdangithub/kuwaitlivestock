# -*- coding: utf-8 -*-
import time
from odoo import api, models, fields
from datetime import datetime
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
import requests
from datetime import datetime, date, time

class Promissory(models.Model):
    _name = 'promissory'

    name_partner_id = fields.Many2one('res.partner', string='العميل')
    amount = fields.Float(string="قيمة القسط", required=True,readonly=True, states={'draft': [('readonly', False)]})
    edit_date = fields.Date(string="تاريخ التحرير", required=True, default=datetime.today(),readonly=True, states={'draft': [('readonly', False)]})
    get_date = fields.Date(string="تاريخ الاستحقاق", required=True, default=datetime.today(),readonly=True, states={'draft': [('readonly', False)]})
    state = fields.Selection([('draft', 'مسوده'), ('open', 'مفتوح'), ('paid', 'مدفوع'), ('tm','تم'), ('cancel', 'ملغي')], string='الحاله', default='draft',readonly=True, states={'draft': [('readonly', False)]})
    journal_sequence = fields.Many2one('ir.sequence', string="تسلسل",readonly=True, states={'draft': [('readonly', False)]})
    source_payment_id = fields.Many2one('account.payment', 'Source payment', readonly=True, states={'draft': [('readonly', False)]})
    date_tsdeed = fields.Date(string="تاريخ التسديد", readonly=True)
    journal_idd = fields.Many2one('account.journal', string="اليوميه")




    def cancel_promissory(self):
        self.write({'state': 'cancel'})

    def cancel_promissory_open(self):
        self.write({'state': 'open'})


    def to_paid(self):
        self.write({'state': 'paid'})
        self.date_tsdeed = datetime.today()
        start_dt = fields.Datetime.from_string(self.get_date)
        finish_dt = fields.Datetime.from_string(self.edit_date)
        tsdeed = fields.Datetime.from_string(self.date_tsdeed)
        a = relativedelta(tsdeed, start_dt)
        self.far8 = str(a.years)+'سنة'+' /  '+str(a.months)+'شهر'+' /  '+str(a.days)+'يوم'



