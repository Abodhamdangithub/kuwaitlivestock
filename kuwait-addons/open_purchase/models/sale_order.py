# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError




class SaleOrder(models.Model):
    _inherit = 'sale.order'


    def action_confirm(self):
        obj = self.order_line.filtered(lambda m: not m.open_purchase_id )
        if obj:
            raise UserError(_('يجب تحديد ارسالية لجميع السطور') )

        super(SaleOrder, self).action_confirm()

