# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError




class StockScrap(models.Model):
    _inherit = 'stock.scrap'



    open_purchase_line_id = fields.Many2one('open.purchase.line',string="open.purchase.line")

    def action_validate(self):
        if self.open_purchase_line_id:
            if self.scrap_qty > self.open_purchase_line_id.qty_available:
                raise UserError(_('لا يمكنك اتلاف كمية اكبر من المتاحه '))
            self.open_purchase_line_id.qty_talef = self.open_purchase_line_id.qty_talef + self.scrap_qty
        super(StockScrap, self).action_validate()
