# -*- coding: utf-8 -*-

from odoo import api, fields, models
import subprocess as sp
import logging
import os
from datetime import datetime

_logger = logging.getLogger(__name__)

class company(models.Model):
    _inherit = 'res.company'

    seq_ticket = fields.Many2one('ir.sequence', 'Secuencia de ticket', copy=False, )
    seq_ticket_fact = fields.Many2one('ir.sequence', 'Secuencia de ticket factura', copy=False, )
    seq_nota_venta = fields.Many2one('ir.sequence', 'Secuencia de nota de venta', copy=False, )
    seq_boleta = fields.Many2one('ir.sequence', 'Secuencia de Boleta electronica', copy=False, )
    seq_factura = fields.Many2one('ir.sequence', 'Secuencia de Factura electronica', copy=False, )
    seq_boleta_venta = fields.Many2one('ir.sequence', 'Secuencia de Boleta', copy=False, )
    seq_factura_venta = fields.Many2one('ir.sequence', 'Secuencia de Factura', copy=False, )
    seq_send_order = fields.Many2one('ir.sequence', 'Secuencia de Envio de pedido', copy=False, )

    def get_seq_id(self, seq_name, vat=False):
        _logger.info("Se obtiene secuencia id con vat:"+(vat or '1'))
        if vat:
            res_company = self.env['res.company'].sudo().search([('vat', '=', vat)])
        else:
            res_company = self.env['res.company'].sudo().search([('id', '=', 1)])
        if not res_company:
            return False
        _logger.info("Se obtiene secuencia res company:" + str(res_company.id))
        if seq_name == 'seq_ticket' and res_company.seq_ticket:
            return res_company.seq_ticket.id
        elif seq_name == 'seq_ticket_fact' and res_company.seq_ticket_fact:
            return res_company.seq_ticket_fact.id
        elif seq_name == 'seq_boleta' and res_company.seq_boleta:
            return res_company.seq_boleta.id
        elif seq_name == 'seq_factura' and res_company.seq_factura:
            return res_company.seq_factura.id
        elif seq_name == 'seq_boleta_venta' and res_company.seq_boleta_venta:
            return res_company.seq_boleta_venta.id
        elif seq_name == 'seq_factura_venta' and res_company.seq_factura_venta:
            return res_company.seq_factura_venta.id
        elif seq_name == 'seq_nota_venta' and res_company.seq_nota_venta:
            return res_company.seq_nota_venta.id
        else:
            return False

    def get_num_seq(self, seq_name, pos_reference, vat=False):
        pos_obj = self.env['pos.order.seq']
        """Devuelve el numero de la secuencia solicitada"""
        seq_id = self.get_seq_id(seq_name, vat)
        pos = pos_obj.sudo().search([('pos_reference', '=', pos_reference)])
        if pos:
            _logger.info("Se retorna numero %s" % pos.numero)
            return pos.numero
        elif seq_id:
            _logger.info("Se obtiene secuencia")
            seq_val = self.env['ir.sequence'].sudo().browse(seq_id).next_by_id()
            if pos_reference:
                pos_obj.sudo().create({'pos_reference': pos_reference, 'numero': seq_val})
            return seq_val
        return False

    def verif_seq(self, seq_name, vat=False):
        """Devuelve el numero de la secuencia solicitada"""
        seq_id = self.get_seq_id(seq_name, vat)
        return seq_id

    def graba_comprobante(self, order):
        """Registra los datos del comprobante para luego imprimirlos"""
        pos_comp = self.env['pos.comprobante']
        if order.get('date_due', False):
            date_due = datetime.strptime(order['date_due'], '%Y-%m-%d').strftime('%d-%m-%Y')
        else:
            date_due = ''
        # Elimina si hay duplicado de comprobante a imprimir
        numero = self.get_num_seq(order['seq_name'], order['pos_reference'])
        pos_comp_obj = pos_comp.sudo().search([('tipo_comprobante', '=', order['tipo_comp']), ('numero', '=', numero)])
        if pos_comp_obj:
            pos_comp_obj.sudo().unlink()
        vals = {
            'fecha_emision': order['date']['localestring'][:10],
            'tipo_comprobante': order['tipo_comp'],
            'numero': numero,
            'numero_original': order['seq_ticket'],
            'razon_social': order['client'],
            'dir_fiscal': order['client_address'],
            'tipo_doc': order['client_doc_type'],
            'nro_doc': order['client_vat'],
            'subtotal': "{:.2f}".format(order['total_without_tax']),
            'igv': "{:.2f}".format(order['total_tax']),
            'total': "{:.2f}".format(order['total_with_tax']),
            'total_letras': order['amount_to_text'],
            'moneda_name': order['currency']['name'],
            'moneda_symbol': order['currency']['symbol'],
            'pos_reference': order['pos_reference'],
            'vendedor': order.get('vendedor', ''),
            'nro_oc': order.get('nro_oc', ''),
            'nro_guia': order.get('nro_guia', ''),
            'date_due': date_due,
            'journal_name': order.get('journal_name', ''),
            'formato': order.get('formato', ''),
        }
        pos_comp_id = pos_comp.sudo().create(vals)
        for line in order['orderlines']:
            vals_line = {
                'codigo': line['product_default_code'],
                'descripcion': line['product_name'],
                'precio_unitario': "{:.3f}".format(line['price']),
                'cantidad': line['quantity'],
                'subtotal': "{:.2f}".format(line['price_without_tax']),
                'total': "{:.2f}".format(line['price_with_tax']),
                'unit_name': line['unit_name'],
                'order_id': pos_comp_id.id,
            }
            self.env['pos.comprobante.line'].sudo().create(vals_line)
        #Graba la cola de impresion
        path_root = os.path.join(os.path.dirname(os.path.abspath(__file__)))
        path_exe = path_root + '\print_odoo_pb9\exe\print_odoo.exe'
        vals_cola = {
            'tipo_comprobante': vals['tipo_comprobante'],
            'numero': vals['numero'],
            'path_exe': path_exe,
            'total': "{:.2f}".format(order['total_with_tax']),
            'razon_social': order['client'],
            'formato': vals.get('formato', ''),
        }
        self.env['pos.comprobante.cola.impresion'].sudo().create(vals_cola)
        #comp = vals['tipo_comprobante']+'&'+vals['numero']
        # try:
        #     _logger.info("Ejecuta print_odoo.exe:"+path_exe)
        #     sp.call([path_exe, comp])
        # except:
        #     _logger.warning("Error al ejecutar print_odoo.exe:"+path_exe)
        return True

    def graba_guia(self, data):
        """Registra los datos del comprobante para luego imprimirlos"""
        pos_comp = self.env['pos.comprobante']
        for guia in data:
            # Elimina si hay duplicado de comprobante a imprimir
            pos_comp_obj = pos_comp.sudo().search([('tipo_comprobante', '=', 'GU'), ('numero', '=', guia['name'])])
            if pos_comp_obj:
                pos_comp_obj.sudo().unlink()
            vals = {
                'fecha_emision': guia['date'],
                'tipo_comprobante': 'GU',
                'numero': guia['name'],
                'razon_social': guia['partner']['display_name'],
                'dir_fiscal': guia['partner']['street'],
                'tipo_doc': guia['partner'].get('tipo_doc', ''),
                'nro_doc': guia['partner']['vat'],
                'motivo_traslado': guia['motivo_traslado'],
                'origin': guia['origin'],
                'transportista': guia['transportista']['name'],
                'transportista_tipo_doc': guia['transportista']['tipo_doc'],
                'transportista_nro_doc': guia['transportista']['vat'],
                'warehouse_street': guia['warehouse_street'],
                'placa_conductor': guia['transportista']['placa_conductor'],
                'lic_conductor': guia['transportista']['lic_conductor'],
                'name_printer': guia.get('name_printer', ''),
                'formato': guia.get('formato', ''),
            }
            pos_comp_id = pos_comp.sudo().create(vals)
            for line in guia['picking_line']:
                vals_line = {
                    'order_id': pos_comp_id.id,
                    'codigo': line['product']['default_code'],
                    'descripcion': line['product']['name'],
                    'cantidad': line['product']['quantity'],
                    'unit_name': line['product']['uom'],
                }
                self.env['pos.comprobante.line'].sudo().create(vals_line)
            # Graba la cola de impresion
            path_root = os.path.join(os.path.dirname(os.path.abspath(__file__)))
            path_exe = path_root + '\print_odoo_pb9\exe\print_odoo.exe'
            vals_cola = {
                'tipo_comprobante': vals['tipo_comprobante'],
                'numero': vals['numero'],
                'path_exe': path_exe,
                'razon_social': guia['partner']['display_name'],
                'formato': vals.get('formato', ''),
            }
            self.env['pos.comprobante.cola.impresion'].sudo().create(vals_cola)
        return True

    def graba_invoice(self, data):
        """Registra los datos del comprobante para luego imprimirlos
        es llamado desde el modelo account.invoice
        """
        pos_comp = self.env['pos.comprobante']
        for invoice in data:
            # Elimina si hay duplicado de comprobante a imprimir
            pos_comp_obj = pos_comp.sudo().search([('tipo_comprobante', '=', invoice['tipo_comp']), ('numero', '=', invoice['number'])])
            if pos_comp_obj:
                pos_comp_obj.sudo().unlink()
            vals = {
                'fecha_emision': invoice['date'],
                'tipo_comprobante': invoice['tipo_comp'],
                'numero': invoice['number'],
                'razon_social': invoice['partner']['display_name'],
                'dir_fiscal': invoice['partner']['street'],
                'tipo_doc': invoice['partner'].get('tipo_doc', ''),
                'nro_doc': invoice['partner']['vat'],
                'subtotal': invoice['amount_untaxed'],
                'igv': invoice['amount_tax'],
                'total': invoice['amount_total'],
                'total_letras': invoice['amount_text'],
                'moneda_name': invoice['currency']['name'],
                'moneda_symbol': invoice['currency']['symbol'],
                'vendedor': invoice.get('vendedor', ''),
                'nro_oc': invoice.get('orden_compra', ''),
                'nro_guia': invoice.get('guia_remision', ''),
                'date_due': invoice['date_due'],
                'journal_name': invoice.get('termino_pago', ''),
                'formato': invoice.get('formato', ''),
            }
            pos_comp_id = pos_comp.sudo().create(vals)
            for line in invoice['invoice_line']:
                vals_line = {
                    'codigo': line['product']['default_code'],
                    'descripcion': line['product']['name'],
                    'precio_unitario': line['product']['price_unit_str'],
                    'cantidad': line['product']['quantity'],
                    'subtotal': line['product']['price_subtotal_str'],
                    'total': line['product']['total'],
                    'unit_name': line['product']['product_uom'],
                }
                self.env['pos.comprobante.line'].sudo().create(vals_line)
            # Graba la cola de impresion
            path_root = os.path.join(os.path.dirname(os.path.abspath(__file__)))
            path_exe = path_root + '\print_odoo_pb9\exe\print_odoo.exe'
            vals_cola = {
                'tipo_comprobante': vals['tipo_comprobante'],
                'numero': vals['numero'],
                'path_exe': path_exe,
                'total': vals['total'],
                'razon_social': vals['razon_social'],
                'formato': vals['formato'],
            }
            self.env['pos.comprobante.cola.impresion'].sudo().create(vals_cola)
        return True

    def graba_letter(self, data):
        pos_comp = self.env['pos.comprobante']
        for letter in data:
            # Elimina si hay duplicado de comprobante a imprimir
            pos_comp_obj = pos_comp.sudo().search(
                [('tipo_comprobante', '=', letter['tipo_comp']), ('numero', '=', letter['number'])])
            if pos_comp_obj:
                pos_comp_obj.sudo().unlink()
            vals = {
                'fecha_emision': letter['date'],
                'tipo_comprobante': letter['tipo_comp'],
                'numero': letter['number'],
                'razon_social': letter['partner']['display_name'],
                'dir_fiscal': letter['partner']['street'],
                'tipo_doc': letter['partner'].get('tipo_doc', ''),
                'nro_doc': letter['partner']['vat'],
                'telefono': letter['partner']['telefono'],
                'total': letter['amount_total'],
                'total_letras': letter['amount_text'],
                'moneda_name': letter['currency']['name'],
                'moneda_symbol': letter['currency']['symbol'],
                'date_due': letter['date_due'],
                'origin': letter['origin'],
                'formato': letter.get('formato', ''),
            }
            pos_comp_id = pos_comp.sudo().create(vals)
            # Graba la cola de impresion
            path_root = os.path.join(os.path.dirname(os.path.abspath(__file__)))
            path_exe = path_root + '\print_odoo_pb9\exe\print_odoo.exe'
            vals_cola = {
                'tipo_comprobante': vals['tipo_comprobante'],
                'numero': vals['numero'],
                'path_exe': path_exe,
                'total': vals['total'],
                'razon_social': vals['razon_social'],
                'formato': vals['formato'],
            }
            self.env['pos.comprobante.cola.impresion'].sudo().create(vals_cola)
        return True