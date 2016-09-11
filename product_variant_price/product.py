# -*- coding: utf-8 -*-

from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class product_template(osv.osv):
    _inherit = "product.template"

    def _price_get(self, cr, uid, products, ptype='list_price', context=None):
        res = super(product_template, self)._price_get(cr, uid, products, ptype=ptype, context=None)
        if 'currency_id' in context:
            pricetype_obj = self.pool.get('product.price.type')
            price_type_id = pricetype_obj.search(cr, uid, [('field', '=', ptype)])[0]
            price_type_currency_id = pricetype_obj.browse(cr, uid, price_type_id).currency_id.id

        product_uom_obj = self.pool.get('product.uom')
        for product in products:#Recorro de nuevo
            if product.fixed_price_variant and ptype == 'list_price':#Si coge precio fijo
                res[product.id] = product.fixed_price
            if 'uom' in context:
                uom = product.uom_id or product.uos_id
                res[product.id] = product_uom_obj._compute_price(cr, uid,
                                                                 uom.id, res[product.id], context['uom'])
            if 'currency_id' in context:
                # Take the price_type currency from the product field
                # This is right cause a field cannot be in more than one currency
                res[product.id] = self.pool.get('res.currency').compute(cr, uid, price_type_currency_id,
                                                                        context['currency_id'], res[product.id],
                                                                        context=context)
        return res

class product_product(osv.osv):
    _inherit = "product.product"

    def _set_product_lst_price(self, cr, uid, id, name, value, args, context=None):
        res = super(product_product, self)._set_product_lst_price(cr, uid, id, name, value, args, context=context)
        return res

    def _product_lst_price(self, cr, uid, ids, name, arg, context=None):
        res = super(product_product, self)._product_lst_price(cr, uid, ids, name, arg, context=context)
        for product in self.browse(cr, uid, ids, context=context):
            if product.fixed_price_variant:
                res[product.id] = product.fixed_price
        return res

    _columns = {
        'fixed_price_variant': fields.boolean('Fijar precio:', help="Precio fijo para la variante. Se ignora el precio extra de los atributos"),
        'fixed_price': fields.float('Fijar precio en', digits_compute=dp.get_precision('Product Price'),),
        'lst_price': fields.function(_product_lst_price, fnct_inv=_set_product_lst_price, type='float',
                                     string='Public Price', digits_compute=dp.get_precision('Product Price')),
    }