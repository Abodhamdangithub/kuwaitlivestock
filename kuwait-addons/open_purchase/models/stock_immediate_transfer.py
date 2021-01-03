# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, _
from odoo.exceptions import UserError


class StockImmediateTransfer(models.TransientModel):
    _inherit = 'stock.immediate.transfer'


    def process(self):
        purchase_id = self.env['purchase.order'].search([('name', '=', self.pick_ids.origin)])
        if purchase_id:
            if not purchase_id.open_purchase_ids:
                purchase_id.create_open_purchase()
        return super(StockImmediateTransfer, self).process()

