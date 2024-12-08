# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'Refresca la lista de directorio del attachment en caso de error de lectura ',
    'version': '1.0',
    'category': 'Extra Tools',
    'sequence': 6,
    'summary': '',
    'description': """
    En GlusterFS al leer un archivo del filestore hay problemas con la lectura indicando que no existe el archivo, esto es un
    problema de actualizacion del metadato.
""",
    'depends': ['base'],
    'website': 'vmcloudsolution.pe',
    'data': [
    ],
    'installable': True,
    'auto_install': False,
}
