# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'JExcel',
    'version': '1.0',
    'category': 'Extra Tools',
    'sequence': 6,
    'summary': '',
    'description': """
""",
    'depends': ['base'],
    'website': 'vmcloudsolution.pe',
    'data': [
        'views/jexcel_templates.xml',
    ],
    'qweb': [
        'static/src/xml/pos.xml',
    ],
    'installable': True,
    'auto_install': False,
}
