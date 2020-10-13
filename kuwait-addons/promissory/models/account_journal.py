# -*- coding: utf-8 -*-
from odoo import api, models, fields


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    type = fields.Selection(selection_add=[('promissory', 'كمبيالات'),('tsdeed_promissory', 'تسديد كمبيالة'),('check', 'شيك')])