# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Odoo 13 purchase K',
    'version': '13.0.2.0.1',
    'category': 'purchase',
    'summary': 'Purchase And All Edition',
    'sequence': '8',
    'author': 'Abdelraheem Hamdan',
    'maintainer': 'Odoo Mates',
    'license': 'LGPL-3',
    'support': 'odoomates@gmail.com',
    'website': '',
    'depends': ['purchase','sale','account','fleet','stock'],
    'demo': [],
    'data': [
        'security/security.xml',
        'wizard/stock_scrap.xml',
        'views/account_bank_statement.xml',
        'views/purchase_order.xml',
        'views/res_partner.xml',
        'views/open_purchase.xml',
        'wizard/wizard_set_open_purchase.xml',
        'views/sale_order.xml',
        'views/fleet_vehicle.xml',
        'views/moving_form.xml',
        'views/account_move.xml',
        'security/ir.model.access.csv',
        'views/sequance.xml',
        'report/report.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'images': [''],
    'qweb': [],
}
