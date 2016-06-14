# -*- coding: utf-8 -*-

##############################################################################
#
#    This module copyright :
#        (c) 2016 VMCloud Solution (http://vmcloudsolution.pe)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import api

class account_invoice(osv.osv):
    _inherit = "account.invoice"

    _columns = {
        'warehouse_id': fields.many2one('stock.warehouse', 'Warehouse'),
        'picking_id': fields.many2one('stock.picking', 'Orden de entrega', 'Orden de entrega asociado', copy=False),
    }

    def _default_warehouse(self, cr, uid, context=None):
        print 'padre'
        return False

    _defaults = {
        'warehouse_id': _default_warehouse,
    }

    def _get_picking_type_out(self, cr, uid, warehouse_id, context=None):
        picking_type_id = self.pool.get('stock.picking.type', self).search(cr, uid, [('warehouse_id', '=', warehouse_id), ('code', '=', 'outgoing')], context=context, limit=1)
        return picking_type_id

    def create_picking(self, cr, uid, ids, context=None):
        """Create a picking for each invoice and validate it."""
        picking_obj = self.pool.get('stock.picking')
        picking_type_obj = self.pool.get('stock.picking.type')
        partner_obj = self.pool.get('res.partner')
        move_obj = self.pool.get('stock.move')
        picking_id = None
        for invoice in self.browse(cr, uid, ids, context=context):
            if not invoice.warehouse_id.id:
                raise osv.except_osv('Verifique!', 'Seleccione un Almacén')
            if all(t == 'service' for t in invoice.invoice_line.mapped('product_id.type')):
                continue
            addr = invoice.partner_id and partner_obj.address_get(cr, uid, [invoice.partner_id.id], ['delivery']) or {}
            picking_type_id = self._get_picking_type_out(cr, uid, invoice.warehouse_id.id, context=context)
            if not picking_type_id:
                raise osv.except_osv('Error!', _('No se pudo encontrar el tipo de operacion Salida para %s. Puede deverse a que no cuenta con el acceso a dicho almacen o no esta configurado.' % (invoice.warehouse_id.name,)))
            picking_type_obj = picking_type_obj.browse(cr, uid, picking_type_id, context=context)
            picking_id = picking_obj.create(cr, uid, {
                'origin': invoice.number,
                'partner_id': addr.get('delivery',False),
                'date_done': invoice.date_invoice,
                'picking_type_id': picking_type_obj.id,
                'company_id': invoice.company_id.id,
                'move_type': 'direct',
                'note': invoice.comment or "",
                'invoice_state': 'none',
            }, context=context)
            self.write(cr, uid, [invoice.id], {'picking_id': picking_id}, context=context)
            location_id = invoice.warehouse_id.lot_stock_id.id
            destination_id = invoice.partner_id.property_stock_customer.id
            if not destination_id:
                destination_id = picking_type_obj.default_location_dest_id.id
            else:
                destination_id = partner_obj.default_get(cr, uid, ['property_stock_customer'], context=context)['property_stock_customer']
            move_list = []
            for line in invoice.invoice_line:
                if line.product_id and line.product_id.type == 'service':
                    continue
                move_list.append(move_obj.create(cr, uid, {
                    'name': line.name,
                    'product_uom': line.product_id.uom_id.id,
                    'product_uos': line.product_id.uom_id.id,
                    'picking_id': picking_id,
                    'picking_type_id': picking_type_obj.id,
                    'product_id': line.product_id.id,
                    'product_uos_qty': abs(line.quantity),
                    'product_uom_qty': abs(line.quantity),
                    'state': 'draft',
                    'location_id': location_id if line.quantity >= 0 else destination_id,
                    'location_dest_id': destination_id if line.quantity >= 0 else location_id,
                }, context=context))
            if picking_id:
                picking_obj.action_confirm(cr, uid, [picking_id], context=context)
                picking_obj.force_assign(cr, uid, [picking_id], context=context)
                picking_obj.action_done(cr, uid, [picking_id], context=context)
            elif move_list:
                move_obj.action_confirm(cr, uid, move_list, context=context)
                move_obj.force_assign(cr, uid, move_list, context=context)
                move_obj.action_done(cr, uid, move_list, context=context)
        return picking_id

    def action_create_delivery_order(self, cr, uid, ids, context=None):
        picking_id = self.create_picking(cr, uid, ids, context=context)
        if not picking_id:
            raise osv.except_osv('Error!', _('Cannot create picking'))
        return True

    def _get_picking_type_returns(self, cr, uid, invoice_id, context=None):
        invoice_obj = self.pool.get('account.invoice').browse(cr, uid, invoice_id, context=context)
        pick_type_id = invoice_obj.picking_id.picking_type_id.return_picking_type_id and invoice_obj.picking_id.picking_type_id.return_picking_type_id.id or invoice_obj.picking_id.picking_type_id.id
        return pick_type_id

    def create_returns(self, cr, uid, invoice_obj, context=None):
        move_obj = self.pool.get('stock.move')
        pick_obj = self.pool.get('stock.picking')
        new_picking = pick_obj.copy(cr, uid, invoice_obj.picking_id.id, {
            'move_lines': [],
            'picking_type_id': self._get_picking_type_returns(cr, uid, invoice_obj.id, context=context),
            'state': 'draft',
            'origin': invoice_obj.picking_id.name,
        }, context=context)
        move_list = []
        for move in invoice_obj.picking_id.move_lines:
            new_move_id = move_obj.copy(cr, uid, move.id, {
                'picking_id': new_picking,
                'state': 'draft',
                'location_id': move.location_dest_id.id,
                'location_dest_id': move.location_id.id,
                'origin_returned_move_id': move.id,
                'procure_method': 'make_to_stock',
                })
            move_list.append(new_move_id)
        if new_picking:
            pick_obj.action_confirm(cr, uid, [new_picking], context=context)
            pick_obj.force_assign(cr, uid, [new_picking], context=context)
            pick_obj.action_done(cr, uid, [new_picking], context=context)
        elif move_list:
            move_obj.action_confirm(cr, uid, move_list, context=context)
            move_obj.force_assign(cr, uid, move_list, context=context)
            move_obj.action_done(cr, uid, move_list, context=context)
        return new_picking

    def action_cancel(self, cr, uid, ids, context=None):
        pick_obj = self.pool.get('stock.picking')
        for invoice in self.browse(cr, uid, ids, context=context):
            if invoice.picking_id.state == 'done':
                new_picking = self.create_returns(cr, uid, invoice, context=context)
                if pick_obj.browse(cr, uid, new_picking, context=context).state != 'done':
                    raise osv.except_osv('Error!', _('You cannot cancel an invoice that has a picking without reversing.'))
                invoice.write({'picking_id': False}, context=context)
        return super(account_invoice, self).action_cancel(cr, uid, ids, context=context)

# class sale_configuration(osv.TransientModel):
#     _inherit = 'sale.config.settings'
#
#     _columns = {
#         'picking_automatic': fields.boolean('Create picking automatically', implied_group='account_invoice_picking.group_picking_automatic', help='Allows create picking automatically to validate invoice'),
#     }