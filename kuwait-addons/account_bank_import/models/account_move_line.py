# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
from odoo.exceptions import UserError, ValidationError

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'


    account_add_custody_id = fields.Many2one('account.add.custody', string="account.add.custody")

