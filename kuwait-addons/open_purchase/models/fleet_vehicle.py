# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    moving_form_ids = fields.One2many('moving.form','fleet_vehicle_id', readonly=False,invisible=True)
    moving_form_count = fields.Integer(compute='_compute_fleet_vehicle_count')

    account_expense = fields.Many2one('account.account',string="حساب المصروف")
    account_revenues = fields.Many2one('account.account',string="حساب الايرادات")
    comm = fields.Float(string="نسبة العمولة")

    def create_fleet_vehicle(self):
        create_open_purcahse = self.env["moving.form"].create({"fleet_vehicle_id": self.id,"driver_id": self.driver_id.id})
        return self.action_view_vehicle(create_open_purcahse)

    def action_view_vehicle(self,create_open_purcahse):
        return {
            'view_mode': 'form',
            'view_id': self.env.ref('open_purchase.moving_form_view_form').id,
            'res_model': 'moving.form',
            'context': {
                'default_fleet_vehicle_id': self.id,
                'default_driver_id': self.driver_id.id,
            },
            'type': 'ir.actions.act_window',
            'id': create_open_purcahse.id,
                }

    def _compute_fleet_vehicle_count(self):
        for p in self:
            p.moving_form_count = len(self.moving_form_ids)

    def action_view_moving_form(self):
        moving_form_ids = self.mapped('moving_form_ids')
        action = self.env.ref('open_purchase.moving_form_action').read()[0]
        if len(moving_form_ids) > 1:
            action['domain'] = [('id', 'in', moving_form_ids.ids)]
        elif len(moving_form_ids) == 1:
            form_view = [(self.env.ref('open_purchase.moving_form_view_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = moving_form_ids.id
        else:
            action = {'type': 'ir.actions.act_window_close'}

        context = {
        }
        if len(self) == 1:
            context.update({
            })
        action['context'] = context
        return action
