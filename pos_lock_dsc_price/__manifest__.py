# -*- coding: utf-8 -*-


{
    'name': 'Adaptacion de ticket para sunat',
    'version': '1.0.1',
    'category': 'Point Of Sale',
    'description': """
        -Registro de etiquetera
        -Secuencia unica por serie de etiquetera
        -Venta por defecto a clientes varios
        -Secuencia para ticket boleta y ticket factura
        -Formato de ticket segun normativa sunat
        """,
    'author': 'VMCloud Solution',
    'website': 'http://vmcloudsolution.pe',
    'depends': ['point_of_sale'],
	'data': [
        'views/pos_etiquetera_view.xml',
        'views/pos_ticket_templates.xml',
        'security/ir.model.access.csv',
    ],
    'qweb': [
        'static/src/xml/pos.xml',
    ],
    'init_xml': [],
    'demo_xml': [],
    'test': [],
    'installable': True,
}
