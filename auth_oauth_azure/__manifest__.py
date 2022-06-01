# -*- coding: utf-8 -*-
{
    'name': "Auth OAuth Azure",

    'summary': """ Azure AD oAuth2 integration with Odoo
    """,

    'description': """ Azure AD oAuth2 integration with Odoo
    """,

    'author': 'Mint System / GNR GROUP',
    'website': 'https://www.mint-system.ch / https://gnrgroup.co.th',
    'license': 'AGPL-3',
    'category': 'Technical Settings',
    'version': '14.0.1.0.0',

    'depends': [
        'base',
        'auth_oauth',
    ],

    'data': [
        'views/ir_ui_view.xml',
    ],
}
