# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError




class AccountMove(models.Model):
    _inherit = 'account.move'

    open_purchase_id = fields.Many2one('open.purchase', readonly=False, string="الارسالية")
    type_expenses_purchase = fields.Selection([('normal', 'عادي'), ('open_purchase', 'مصروف ارسالية')],string="عادي/مصروف ارسالية",copy=False)
    open_purchase_line_id = fields.Many2one('open.purchase.line', readonly=False, string="منتجات الارسالية")


    def action_post(self):
        result = super(AccountMove, self).action_post()
        for inv in self:
            if  inv.type_expenses_purchase == 'open_purchase' and not inv.open_purchase_id:
                raise UserError(_('يجب ادخال الارسالية التابعه للمصروف'))
        return result
    def button_cancel(self):
        result = super(AccountMove, self).button_cancel()
        for inv in self:
            if  inv.type_expenses_purchase == 'open_purchase' and inv.open_purchase_id:
                inv.open_purchase_id = False
                inv.open_purchase_line_id = False

        return result


