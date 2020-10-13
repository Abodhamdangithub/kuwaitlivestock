# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError




class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    open_purchase_id = fields.Many2one('open.purchase',"الارسالية", readonly=True)
    open_purchas_line_id = fields.Many2one('open.purchase.line',"سطر الارسالية", readonly=True)

    def write(self, vals):
        res = super(SaleOrderLine, self).write(vals)
        if  self.open_purchas_line_id.qty - self.open_purchas_line_id.qty_sales < 0:
            raise UserError(_('لا يوجد كمية للمنتج %s في الارسالية %s  الكمية المتاحة هي %s'%(self.product_id.name,self.open_purchase_id.order_number,self.open_purchas_line_id.qty_available+self.product_uom_qty )) )
        return res

    # @api.onchange('product_uom_qty')
    # def set_price(self):
    #     self.price_unit = self.open_purchas_line_id.price_unit