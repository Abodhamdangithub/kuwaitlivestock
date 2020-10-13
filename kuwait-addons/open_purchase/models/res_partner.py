# -*- coding: utf-8 -*-

from odoo import api, fields, models, _




class ResPartner(models.Model):
    _inherit = 'res.partner'

    account_move_line_ids = fields.One2many('account.move.line','partner_id',string="Move Lines")
    balance_partner = fields.Float(string="الرصيد",compute='_compute_balance_partner')



    @api.depends("account_move_line_ids")
    def _compute_balance_partner(self):
        try:
            for me in self:
                select = "select COALESCE( sum(debit) - sum(credit),0) as balance from account_move_line where partner_id = %s and  (select type from account_account_type where id = (select user_type_id from account_account where id = account_move_line.account_id) )  in ('receivable','payable')" % (me.id)
                me.env.cr.execute(select)
                results = me.env.cr.dictfetchall()[0]['balance']
                me.balance_partner = results
        except:
            print ("Cant Error")
