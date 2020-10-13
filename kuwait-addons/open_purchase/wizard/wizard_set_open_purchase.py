# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError




class WizardSetOpenPurchase(models.Model):
    _name = 'wizard.set.open.purchase'

    open_purchase_id = fields.Many2one('open.purchase',string="الارسالية",required=True)


    def set_open_purchase_to_order_line(self):
        order_line = self.env['sale.order.line'].browse(self.env.context['active_id'])
        order_line.open_purchase_id = self.open_purchase_id.id
        line = self.open_purchase_id.open_purchase_line_ids.filtered(lambda m: m.product_id.id == order_line.product_id.id)
        if line:
            order_line.open_purchas_line_id = line.id
            #order_line.price_unit = line.price_unit
        else:
            raise UserError(_('المنتج غير موجود في هذه الارسالية') )

