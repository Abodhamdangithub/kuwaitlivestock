# -*- coding: utf-8 -*-
from openerp import models, fields, api
from datetime import datetime
from dateutil.relativedelta import relativedelta
import calendar


class res_res_partner(models.Model):

    _inherit = 'res.partner'

    promissory_all = fields.One2many('promissory','name_partner_id', readonly=True, string="كمبيالات العميل")
