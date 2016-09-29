##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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

from openerp import SUPERUSER_ID
from openerp.osv import fields, osv

class pos_order(osv.osv):
    _inherit = 'pos.order'

    # def _get_standard_price_pack(self, cr, uid, product_pack, context=None):
    #     #Retorna el costo acumulado de los productos que componen el pack
    #     product_pack_line_ids = self.pool.get('product.pack.line').search(cr, uid, [('parent_product_id', '=', product_pack)], context=context)
    #     product_pack_cost = 0.00
    #     for pack_id in product_pack_line_ids:
    #         product_pack_line_obj = self.pool.get('product.pack.line').browse(cr, uid, pack_id, context=context)
    #         product_pack_cost += product_pack_line_obj.product_id.standard_price
    #     return product_pack_cost

    def set_gross_margin(self, cr, order, context=None):
        #Obtiene la utilidad del pack cuando el precio de los componentes esta incluido en el pack
        uid = 1
        for line in order.lines:
            if line.product_id.pack and not line.pack_parent_line_id.id:
                product_cost = line.product_id.standard_price
                product_cost_total = line.product_id.standard_price * line.qty
                pack_line_ids = self.pool.get('pos.order.line').search(cr, uid, [('order_id', '=', order.id), ('pack_parent_line_id', '=', line.id)])
                pack_cost_total = 0
                for pack_line in self.pool.get('pos.order.line').browse(cr, uid, pack_line_ids):
                    pack_cost_total += (pack_line.product_id.standard_price * pack_line.qty)
                line.standard_price = product_cost
                line.gross_margin = line.price_subtotal_incl - (product_cost_total + pack_cost_total)
            if line.pack_parent_line_id.id:
                line.standard_price = line.product_id.standard_price
                line.gross_margin = 0 #El costo ya esta en el pack padre
        return True

    def write(self, cr, uid, ids, vals, context=None):
        result = super(pos_order, self).write(cr, uid, ids, vals, context)
        #OJO: aun no tiene soporte para packs anidados: pack_depth
        #Graba el margen al pasar a estado pagado
        for order in self.browse(cr, uid, ids, context):
            if order.state == 'paid':
                self.set_gross_margin(cr, order, context=context)
        return result

    def init(self, cr):
        update = False #Para que se ejecute en caso de actualizar data historica
        if update:
            cr.execute("""
                    select 	DISTINCT pos_order.id
                    from 	pos_order, pos_order_line, product_product
                    where 	pos_order.id = pos_order_line.order_id
                        and pos_order_line.product_id = product_product.id
                        and pos_order.state in('paid','done','invoiced')
                        /*and exists(select 1 from product_template
                                where product_template.id=product_product.product_tmpl_id
                                    and pack is True
                                )*/
                        and coalesce(standard_price,0)=0
                        --and pos_order.name='TGAMA/0843'
	                """)
            order_ids = map(lambda x: x[0], cr.fetchall())
            for order_id in order_ids:
                order = self.browse(cr, SUPERUSER_ID, order_id, context=None)
                self.set_gross_margin(cr, order)