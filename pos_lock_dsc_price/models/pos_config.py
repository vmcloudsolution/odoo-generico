# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError

class PosConfig(models.Model):
    _inherit = "pos.config"

    pos_etiquetera_id = fields.Many2one('pos.etiquetera', 'Etiquetera Asignada', required=False, domain="[('active', '=', True)]")
    raz_social = fields.Char('Razón Social', size=60, help="Reemplaza a la Razon Social de la Empresa")
    RUC = fields.Char('RUC', size=60, help="Reemplaza al RUC de la Empresa")
    shop_dir_fiscal = fields.Char('Dirección Fiscal', size=100, help="Reemplaza a la direccion fiscal de la empresa el cual se imprime en la cabecera")
    phone = fields.Char('Teléfono', size=50, help="Teléfono")
    shop_dir = fields.Char('Dirección', size=100, help="Dirección del la tienda")
    width_ticket = fields.Integer('Ancho del ticket', default=33, help="Ancho del ticket en caracteres")
    nro_copy = fields.Integer('Copias del ticket', default=1, help="Numero de copias que imprimira el ticket. Esto es util cuando se trata de papel termico")