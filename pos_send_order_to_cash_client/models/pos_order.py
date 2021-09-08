# -*- coding: utf-8 -*-

from odoo import api, fields, models
import json
import logging
_logger = logging.getLogger(__name__)

class PosComprobante(models.Model):
    _name = 'pos.comprobante'

    fecha_emision = fields.Char('Fecha de emision')
    tipo_comprobante = fields.Char('Tipo de comprobante')
    numero = fields.Char('Numero de comprobante')
    numero_original = fields.Char('Numero original')
    razon_social = fields.Char('Razón social del cliente')
    dir_fiscal = fields.Char('Direccion del cliente')
    tipo_doc = fields.Char('Tipo de documento')
    nro_doc = fields.Char('Numero de documento')
    subtotal = fields.Char('Subtotal')
    igv = fields.Char('Igv')
    total = fields.Char('Total')
    total_letras = fields.Char('Total en letras')
    moneda_name = fields.Char('Moneda')
    moneda_symbol = fields.Char('Simbolo moneda')
    pos_reference = fields.Char('pos_reference')
    vendedor = fields.Char('Vendedor')
    nro_oc = fields.Char('Orden de compra')
    nro_guia = fields.Char('Nro de Guía')
    date_due = fields.Char('Fecha de vencimiento')
    journal_name = fields.Char('Nombre forma de pago', help='El el nombre de la primera forma de pago seleccionad, es usada paa pagos a credito o letras No efectivo')
    motivo_traslado = fields.Char('Motivo de traslado')
    origin = fields.Char('Documento origen')
    transportista = fields.Char('Transportista')
    transportista_tipo_doc = fields.Char('Transportista documento')
    transportista_nro_doc = fields.Char('Transportista Vat')
    warehouse_street = fields.Char('Direccion de origen')
    placa_conductor = fields.Char('placa_conductor')
    lic_conductor = fields.Char('lic_conductor')
    name_printer = fields.Char('name_printer')
    telefono = fields.Char('telefono del cliente')


class PosComprobanteLine(models.Model):
    _name = 'pos.comprobante.line'

    codigo = fields.Char('Codigo')
    descripcion = fields.Text('Descripcion')
    precio_unitario = fields.Char('Precio unitario')
    cantidad = fields.Char('Cantidad')
    subtotal = fields.Char('subtotal')
    total = fields.Char('Total')
    unit_name = fields.Char('unit_name')
    order_id = fields.Many2one('pos.comprobante', string='comprobante ref', ondelete='cascade', index=True)

class PosComprobanteColaImpresion(models.Model):
    _name = 'pos.comprobante.cola.impresion'

    tipo_comprobante = fields.Char('Tipo de comprobante')
    numero = fields.Char('Numero de comprobante')
    imprimio = fields.Boolean('Imprimio', default=False)
    path_exe = fields.Char('Path exe')
    total = fields.Char('Total')
    razon_social = fields.Char('Razón social del cliente')
    formato = fields.Char('Formato')

class PosOrderSeq(models.Model):
    """Almacena el id del pedido y su correlativo asignado
    En caso de concurrencia o llamadas duplicadas del mismo pedido se devuelve la secuencia asignada
    """
    _name = 'pos.order.seq'

    pos_reference = fields.Char('pos_reference', index=True)
    numero = fields.Char('Numero de comprobante')

class PosOrderSend(models.Model):
    _name = 'pos.order.send'

    name = fields.Char('Nombre')
    seq_pedido = fields.Char('Secuencia del pedido')
    session_id = fields.Integer('ID Session', help='ID de la session que esta enviando el pedido')
    process = fields.Boolean('¿Procesado?', default=False)
    table_id = fields.Integer('Mesa')

    def save_order(self, data, vat=False):
        #Crea la columna si no existe
        self._cr.execute("""
            SELECT 1
            FROM information_schema.columns
            WHERE table_name='pos_order_send' and column_name='json_order';
        """)
        column_receipt = self._cr.fetchall()
        if not column_receipt:
            self._cr.execute("""
                alter table pos_order_send add column json_order json;
            """)
        #Graba los datos
        if vat:
            res_company = self.env['res.company'].sudo().search([('vat', '=', vat)])
        else:
            res_company = self.env['res.company'].sudo().search([('id', '=', 1)])
        if not res_company.seq_send_order.id:
            _logger.info("Secuencia de Envio de Pedido no definida")
            return False
        seq_val = False
        if not data.get('no_get_seq_val', False):
            pos_order_send = self.sudo().search([('name', '=', data['name'])])  # Elimina si existe el pedido
            seq_val = self.env['ir.sequence'].sudo().browse(res_company.seq_send_order.id).next_by_id()
            if data.get('table', False) and data.get('floor', False):
                seq_val = data['floor']+' - '+data['table']+' - '+seq_val
            if pos_order_send:
                pos_order_send.write({'session_id': data['pos_session_id']})
            else:
                pos_order_send = self.sudo().create({'session_id': data['pos_session_id'], 'name': data['name'], 'seq_pedido': seq_val})
        elif data.get('no_get_seq_val', False) and data.get('table_id', False):
            pos_order_send = self.sudo().search([('name', '=', data['name'])])  # Elimina si existe el pedido
            if pos_order_send:
                pos_order_send.write({'session_id': data['pos_session_id']})
            else:
                if data.get('table', False) and data.get('floor', False):
                    seq_val = data['floor'] + ' - ' + data['table']
                pos_order_send = self.sudo().create({'session_id': data['pos_session_id'], 'name': data['name'], 'seq_pedido': seq_val})
        JSON = json.dumps(data)
        JSON = JSON.decode('latin1')
        self._cr.execute("""
            update pos_order_send set json_order=(%s)
            where id=(%s)
        """, (JSON, pos_order_send.id))
        return seq_val

    def load_order_cash(self, session_id):
        jsons = []
        orders = self.sudo().search([('session_id', '=', session_id), ('process', '=', False)], order='seq_pedido desc')
        for order in orders:
            self._cr.execute("""
                select 	json_order
                from	pos_order_send
                where	id = (%s)
            """, (order.id,))
            result = self._cr.fetchone()[0]
            if type(result) == str:
                result = json.loads(result)
            result['seq_pedido'] = order.seq_pedido
            jsons.append(result)
        return jsons

    def process_order_cash(self, name):
        pos_order = self.sudo().search([('name', '=', name)])
        if pos_order:
            pos_order.write({'process': True})
        return True