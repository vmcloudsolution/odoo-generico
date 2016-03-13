# -*- encoding: latin-1 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
from openerp import fields, models
from openerp.osv import fields as old_fields, osv
from openerp.tools.translate import _
import math


class product_pack(models.Model):
    _name = 'product.pack.line'
    _rec_name = 'product_id'

    parent_product_id = fields.Many2one(
        'product.product', 'Parent Product',
        ondelete='cascade', required=True)
    quantity = fields.Float(
        'Quantity', required=True)
    product_id = fields.Many2one(
        'product.product', 'Product', required=True)

    _sql_constraints = [
        ('uniq_name', 'unique(parent_product_id,product_id)', "Un producto no puede ser parte de sí mismo dentro del pack."),
    ]


    def create(self, cr, uid, values, context=None):
        if values['parent_product_id'] == values['product_id']:
            raise osv.except_osv('Error!',"Un producto no puede ser parte de sí mismo dentro del pack.")
        return super(product_pack, self).create(cr, uid, values, context=context)

class product_product(models.Model):
    _inherit = 'product.product'

    pack_line_ids = fields.One2many(
        'product.pack.line', 'parent_product_id', 'Pack Products',
        help='List of products that are part of this pack.')

    def _product_available(self, cr, uid, ids, field_names=None, arg=False, context=None):
        pack_product_ids = self.search(cr, uid, [
            ('pack', '=', True),
            ('id', 'in', ids),
        ])
        res = super(product_product, self)._product_available(
            cr, uid, list(set(ids) - set(pack_product_ids)),
            field_names, arg, context)
        for product in self.browse(cr, uid, pack_product_ids, context=context):
            pack_qty_available = []
            pack_virtual_available = []
            for subproduct in product.pack_line_ids:
                subproduct_stock = self._product_available(
                    cr, uid, [subproduct.product_id.id], field_names, arg,
                    context)[subproduct.product_id.id]
                sub_qty = subproduct.quantity
                if sub_qty:
                    pack_qty_available.append(math.floor(
                        subproduct_stock['qty_available'] / sub_qty))
                    pack_virtual_available.append(math.floor(
                        subproduct_stock['virtual_available'] / sub_qty))
            # TODO calcular correctamente pack virtual available para negativos
            res[product.id] = {
                'qty_available': min(pack_qty_available),
                'incoming_qty': 0,
                'outgoing_qty': 0,
                'virtual_available': max(min(pack_virtual_available), 0),
            }
        return res

    def _search_product_quantity(self, cr, uid, obj, name, domain, context):
        return super(product_product, self)._search_product_quantity(
            cr, uid, obj, name, domain, context)
    
    #Activar Columns para que el stock del producto este en referencua al minimo de las existencias de uno de los productos que pertenezca al pack
    #_columns = {
    #    'qty_available': old_fields.function(
    #        _product_available, multi='qty_available',
    #        fnct_search=_search_product_quantity),
    #    'virtual_available': old_fields.function(
    #        _product_available, multi='qty_available',
    #        fnct_search=_search_product_quantity),
    #    'incoming_qty': old_fields.function(
    #        _product_available, multi='qty_available',
    #        fnct_search=_search_product_quantity),
    #    'outgoing_qty': old_fields.function(
    #        _product_available, multi='qty_available',
    #        fnct_search=_search_product_quantity),
    #}


class product_template(models.Model):
    _inherit = 'product.template'

    pack_price_type = fields.Selection([
        ('components_price', 'Precio Compuesto'),
        #('totalice_price', 'Totalice Price'),
        ('fixed_price', 'Precio Fijo'),
    ],
        'Pack Price Type',
        help="""        
        * Fixed Price: El precio del pack
        * Components Price: Pack compuesto por el precio de los productos; Ejm: producto1 =10 , producto2=5, Total precio=15;
        """
    )
    sale_order_pack = fields.Boolean(
        'Sale Order Pack',
        help='Sale order are packs used on sale orders to calculate a price of a line',
    )
    pack = fields.Boolean(
        'Pack?',
        help='TODO',
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
