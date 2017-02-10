# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError

class PosOrder(models.Model):
    _inherit = 'pos.order'

    vendedor_id = fields.Many2one('res.users', 'Vendedor')
    #pos_etiquetera_id = fields.Many2one('pos.etiquetera', 'Etiquetera Ref', required=False)
    #pos_etiquetera_corr = fields.Integer('Correlativo', help="Correlativo Etiquetera")
    doc_ori = fields.Char('Documento Origen', readonly=True, copy=False)
    amount_total_rpt = fields.Float('Total pedido', readonly=True, copy=False)
    #total_paid_rpt = fields.Float('Total pagado', readonly=True, copy=False)
    tipo_doc = fields.Selection([('TB', 'Ticket boleta'),
                                 ('TF', 'Ticket factura'),
                                 ('BV', 'Boleta'),
                                 ('FV', 'Factura'), ], 'Tipo de documento', readonly=True, required=True, states={'draft': [('readonly', False)]})
    num_doc = fields.Char('Número de documento', readonly=True)
    to_invoice = fields.Boolean('Factura', default=False)

    @api.model
    def _order_fields(self, ui_order):
        res = super(PosOrder, self)._order_fields(ui_order)
        res['to_invoice'] = ui_order['to_invoice']
        return res

    @api.model
    def create_from_ui(self, orders):
        order_ids = super(PosOrder, self).create_from_ui(orders)
        pos_etiquetera = self.env['pos.etiquetera']
        for order in self.browse(order_ids):
            #Define el correlativo del ticket
            to_invoice = bool(order.to_invoice)
            if order.state == 'paid':
                if not order.session_id.config_id.pos_etiquetera_id:
                    raise ValidationError("El Punto de Venta no tiene configurado una etiquetera.")
                seq_ticket = pos_etiquetera.get_seq_ticket(order.session_id.config_id.pos_etiquetera_id.id, to_invoice)
                tipo_doc = 'TB'
                if to_invoice:
                    tipo_doc = 'TF'
                vals = {'tipo_doc': tipo_doc, 'num_doc': seq_ticket}
                if not order.partner_id:
                    vals['partner_id'] = order.session_id.config_id.pos_etiquetera_id.partner_id.id
                order.write(vals)
        return order_ids

    @api.multi
    def action_pos_order_paid(self):
        res = super(PosOrder, self).action_pos_order_paid()
        self.write({'amount_total_rpt': self.amount_total})
        return res

    @api.multi
    def action_pos_order_invoice(self):
        """
            Para ticket no se genera factura
        """
        return True

class pos_order_line(models.Model):
    _inherit = 'pos.order.line'

    list_price_id = fields.Integer('lp_id', help="Lista de precio ID")
    #price_subtotal = fields.function(compute='_amount_line_all', multi='pos_order_line_amount', digits_compute=dp.get_precision('Product Price'), string='Subtotal w/o Tax', store=True)
    #price_subtotal_incl = fields.function(compute='_amount_line_all', multi='pos_order_line_amount', digits_compute=dp.get_precision('Account'), string='Subtotal', store=True)