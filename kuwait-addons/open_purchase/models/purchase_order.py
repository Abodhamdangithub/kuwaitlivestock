# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    open_purchase_ids = fields.Many2one('open.purchase', readonly=False)
    open_purchase_count = fields.Integer(compute='_compute_open_purchase_count')

    def create_open_purchase(self):
        create_open_purcahse = self.env["open.purchase"].create({"purchase_id": self.id})
        for line in self.order_line:
            self.env["open.purchase.line"].create({"open_purchase_id": create_open_purcahse.id,"product_id": line.product_id.id,"qty_not": line.product_qty,"qty_talef": 0.0,"qty": line.product_qty,"price_unit_purchase": line.price_unit,"price_unit_purchase_orginal": line.price_unit})
        self.open_purchase_ids = create_open_purcahse.id


    def _compute_open_purchase_count(self):
        for p in self:
            p.open_purchase_count = len(self.open_purchase_ids)


    def action_view_open_purchase(self):
        open_purchase_ids = self.mapped('open_purchase_ids')
        action = self.env.ref('open_purchase.open_purchase_action').read()[0]
        if len(open_purchase_ids) > 1:
            action['domain'] = [('id', 'in', open_purchase_ids.ids)]
        elif len(open_purchase_ids) == 1:
            form_view = [(self.env.ref('open_purchase.open_purchase_view_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = open_purchase_ids.id
        else:
            action = {'type': 'ir.actions.act_window_close'}

        context = {
        }
        if len(self) == 1:
            context.update({
            })
        action['context'] = context
        return action
