# -*- coding: utf-8 -*-
{
    'name': 'Promissory',
    'version': '13.1',
    'summary': 'promissory',
    'description': '''
    
	 promissory
                   ''',
    'category': 'promissory',
    'author': 'Abdelraheem',
    'website': '',
    'depends': [
        'account','sale'

    ],
    'data': [
             'security/security.xml',
             'security/ir.model.access.csv',
             'views/promissory_view.xml',
             'views/check.xml',
             'views/account_payment_view.xml',
             #'views/account_journal_view.xml',
             'views/res_res_partner_view.xml',

             ],
    'images': ['static/description/icon.png'],
    'installable': True,
    'auto_install': False,

}
