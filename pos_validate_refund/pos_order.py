# -*- coding: utf-8 -*-
import time
from openerp import tools
from openerp.osv import fields, osv
from openerp.tools.translate import _

class pos_order(osv.osv):
    _inherit = "pos.order"

    _columns = {
        'is_refund': fields.boolean('¿Devuelto?', readonly=True),
    }

    _defaults = {
        'is_refund': False,
    }

    def validate_refund(self, cr, uid, ids, context=None):
        """Válida si la orden ya fue devuelta en su totalidad"""
        for order in self.browse(cr, uid, ids, context=context):
            #No permite devolver una devolucion
            if order.doc_ori and order.amount_total < 0:
                raise osv.except_osv('Verifique!', 'No se permite realizar una devolución sobre si misma')
            if order.is_refund:
                raise osv.except_osv('Verifique!', 'Ya realizo la devolución del pedido.')

    def payment_order_refund(self, cr, uid, original_clone_list, context=None):
        #Crea el pago automático segun la orden original
        for orig_clon in original_clone_list:
            order_orig_obj = self.browse(cr, uid, orig_clon[0], context=context)
            order_clone_obj = self.browse(cr, uid, orig_clon[1], context=context)
            for statements_orig_obj in order_orig_obj.statement_ids:
                self.add_payment(cr, uid, order_clone_obj.id, {
                    'amount': -statements_orig_obj.amount,
                    'payment_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'payment_name': _('return'),
                    'journal': statements_orig_obj.journal_id.id,
                }, context=context)
            self.signal_workflow(cr, uid, [order_clone_obj.id], 'paid')

    def set_value_refund(self, cr, uid, original_clone_list, context=None):
        """Setea valores de la devolucion"""
        for orig_clon in original_clone_list:
            order_orig_obj = self.browse(cr, uid, orig_clon[0], context=context)
            self.write(cr, uid, orig_clon[1], {'date_order': order_orig_obj.date_order})
            self.write(cr, uid, orig_clon[1], {'pos_reference': order_orig_obj.pos_reference})
            self.write(cr, uid, orig_clon[0], {'is_refund': True})


    def refund(self, cr, uid, ids, context=None):
        self.validate_refund(cr, uid, ids, context=context)
        retorno = super(pos_order, self).refund(cr, uid, ids, context=context)
        self.set_value_refund(cr, uid, retorno.get('original_clone_list'), context=context)
        self.payment_order_refund(cr, uid, retorno.get('original_clone_list'), context=context)
        return retorno