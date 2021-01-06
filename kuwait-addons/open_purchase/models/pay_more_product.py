# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime


class PayMoreProduct(models.Model):
    _name = 'pay.more.product'
    _rec_name = 'purchase_line_id'

    purchase_line_id = fields.Many2one('purchase.order.line',string="purchase order line")
    qty = fields.Float(string="الكمية",required=True)
    amount = fields.Float(string="قيمة الوحدة",required=True)


    def set_data_added(self):
        old_amount = self.purchase_line_id.price_unit
        old_qty = self.purchase_line_id.product_qty

        avg = ((old_amount * old_qty) + (self.amount * self.qty)) / (old_qty+self.qty)
        self.purchase_line_id.price_unit = avg
        self.purchase_line_id.product_qty = (old_qty + self.qty)