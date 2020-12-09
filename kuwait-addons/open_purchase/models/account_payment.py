# -*- coding: utf-8 -*-

from odoo import api, fields, models, _




class AccountPayment(models.Model):
    _inherit = 'account.payment'

    open_purchase_id = fields.Many2one('open.purchase', readonly=False, string="الارسالية")
