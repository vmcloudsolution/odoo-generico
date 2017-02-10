# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError


class pos_etiquetera(models.Model):
    _name = 'pos.etiquetera'

    name = fields.Char('Descripción de Impresora', size=40, select=1, required=True, help='Descripción de la Impresora para su identificacion')
    serie = fields.Char('Serie de Impresora', size=20, required=True)
    seq_ticket = fields.Many2one('ir.sequence', 'Secuencia de ticket', help="Secuencia correspondiente al ticket, debe ser única para la serie de la impresora. Dejar en blanco para generar automaticamente", copy=False, )
    seq_ticket_fact = fields.Many2one('ir.sequence', 'Secuencia de ticket factura', help="Indique la misma secuencia del ticket si desea utilizar una sola secuencia. Indicar una secuencia diferente si se desea diferenciar el correlativo cuando se emita Factura.", copy=False, )
    aut_sunat = fields.Char('Autorización Sunat', size=20)
    partner_id = fields.Many2one('res.partner', 'Cliente', required=True, help='Cliente por defecto para ventas anonimas(Clientes Varios)')
    active = fields.Boolean(string="Activo", default=True)

    _sql_constraints = [
        ('uniq_name', 'unique(serie)', "La serie de la impresora debe ser unico"),
    ]

    @api.model
    def create(self, values):
        # Crea la secuencia
        seq_ticket = None
        if not values.get('seq_ticket', False):
            ir_sequence = self.env['ir.sequence']
            seq_ticket = ir_sequence.create({
                'name': 'Etiquetera %s %s' % (values['name'], values.get('serie', False)),
                'padding': 6,
                'implementation': 'no_gap',
                'company_id': values.get('company_id', False),
            })
            values['seq_ticket'] = seq_ticket.id
        if not values.get('seq_ticket_fact', False):
            if seq_ticket:
                values['seq_ticket_fact'] = seq_ticket.id
            else:
                values['seq_ticket_fact'] = values['seq_ticket']
        return super(pos_etiquetera, self).create(values)

    def get_seq_ticket(self, id, factura=False):
        pos_etiquetera = self.browse(id)
        if not pos_etiquetera.seq_ticket:
            raise UserError('Secuencia de Ticket no encontrado.')
        id_seq = pos_etiquetera.seq_ticket.id
        if factura:
            id_seq = pos_etiquetera.seq_ticket_fact.id
        obj_sequence = self.env['ir.sequence'].browse(id_seq)
        seq_nro = obj_sequence.next_by_id()
        return seq_nro