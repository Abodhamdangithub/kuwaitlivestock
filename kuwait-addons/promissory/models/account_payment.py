
from odoo import api, models, fields
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

from collections import defaultdict


class account_payment(models.Model):
    _inherit = 'account.payment'

    third_promissory_receipt_ids = fields.One2many('promissory', 'source_payment_id', 'Promissory',  states={'draft': [('readonly', False)]})
    thalek_3n = fields.Many2many('promissory', string="وذلك عن", readonly=True, states={'draft': [('readonly', False)]})
    checks = fields.One2many('check', 'source_payment_id', 'Checks', states={'draft': [('readonly', False)]})

    type_journal = fields.Selection([
            ('sale', 'Sales'),
            ('purchase', 'Purchase'),
            ('cash', 'Cash'),
            ('bank', 'Bank'),
            ('general', 'Miscellaneous'),
            ('promissory', 'كمبيالات'),
            ('tsdeed_promissory', 'تسديد كمبيالة'),
            ('check', 'شيك'),
        ], related="journal_id.type")



    def post(self):
        for line in self.third_promissory_receipt_ids:
            line.state = "open"
        for line in self.thalek_3n:
            line.state = "paid"
        for line in self.checks:
            line.state = "sndook"
        if self.type_journal == "tsdeed_promissory":
            self.destination_account_id = self.journal_id.default_debit_account_id.id

        return super(account_payment, self).post()


    def action_draft(self):

        for line in self.third_promissory_receipt_ids:
            if line.state != 'open':
                raise ValidationError(_('خطأ في حالة الكمبياله'))

            line.state = "draft"
        for line in self.thalek_3n:
            line.state = "open"
        for line in self.checks:
            if line.state != "sndook":
                raise ValidationError(_('خطأ في حالة الشيك'))

            line.state = "draft"

        return super(account_payment, self).action_draft()


