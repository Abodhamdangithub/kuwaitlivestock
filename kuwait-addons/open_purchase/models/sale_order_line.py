# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError




class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    open_purchase_id = fields.Many2one('open.purchase',"الارسالية", readonly=True)
    open_purchas_line_id = fields.Many2one('open.purchase.line',"سطر الارسالية", readonly=True)
    qty_lock = fields.Float('Lock Quantity', copy=False, compute='_compute_qty_lock',  compute_sudo=True, store=True, digits='Product Unit of Lock', default=0.0)


    pecr_of_comm = fields.Float('قيمة العمولة للدلال للوحدة', copy=False, digits='Product Unit of Lock', default=0.0)
    amount_of_comm = fields.Float('قيمة العمولة للدلال', copy=False, digits='Product Unit of Lock', compute='_compute_amount_of_comm',  compute_sudo=True, store=True, default=0.0)

    def write(self, vals):
        res = super(SaleOrderLine, self).write(vals)
        if  self.open_purchas_line_id.qty - self.open_purchas_line_id.qty_sales < 0:
            raise UserError(_('لا يوجد كمية للمنتج %s في الارسالية %s  الكمية المتاحة هي %s'%(self.product_id.name,self.open_purchase_id.order_number,self.open_purchas_line_id.qty_available+self.product_uom_qty )) )
        return res



    @api.depends('pecr_of_comm','product_uom_qty', 'price_unit')
    def _compute_amount_of_comm(self):
        for me in self:
            me.amount_of_comm = me.pecr_of_comm * me.product_uom_qty




    @api.depends('product_uom_qty','move_ids.state', 'move_ids.scrapped', 'move_ids.product_uom_qty', 'move_ids.product_uom')
    def _compute_qty_lock(self):
        for line in self:
            qty = 0
            outgoing_moves, incoming_moves = line._get_outgoing_incoming_moves()
            # for move in outgoing_moves:
            #     if move.state != 'done':
            #         continue
            #     qty += move.product_uom._compute_quantity(move.product_uom_qty, line.product_uom,
            #                                               rounding_method='HALF-UP')
            # for move in incoming_moves:
            #     if move.state != 'done':
            #         continue
            #     qty -= move.product_uom._compute_quantity(move.product_uom_qty, line.product_uom,
            #                                               rounding_method='HALF-UP')
            for move in incoming_moves:
                if move.state != 'done':
                    continue
                qty += move.product_uom._compute_quantity(move.product_uom_qty, line.product_uom,
                                                          rounding_method='HALF-UP')

            line.qty_lock = line.product_uom_qty - qty
