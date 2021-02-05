# -*- coding: utf-8 -*-

from odoo import api, fields, models, _




class AccountMove(models.Model):
    _inherit = 'account.move'

    open_purchase_id = fields.Many2one('open.purchase', readonly=False, string="الارسالية")
    type_expenses_purchase = fields.Selection([('normal', 'عادي'), ('open_purchase', 'مصروف ارسالية')],string="عادي/مصروف ارسالية",copy=False)

    open_purchase_line_id = fields.Many2one('open.purchase.line', readonly=False, string="منتجات الارسالية")


