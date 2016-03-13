##############################################################################
#
#    This module copyright :
#        (c) 2015 VMCloud Solution (http://vmcloudsolution.pe)
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
import openerp.addons.decimal_precision as dp

class pos_order(osv.osv):
    _inherit = 'pos.order'

    def write(self, cr, uid, ids, vals, context=None):
        result = super(pos_order, self).write(cr, uid, ids, vals, context)
        #Graba el margen al pasar a estado pagado
        for order in self.browse(cr, uid, ids, context):
            if order.state == 'paid':
                for line in order.lines:
                    line.standard_price = line.product_id.standard_price
                    line.gross_margin = line.price_subtotal_incl - (line.product_id.standard_price * line.qty)
        return result

class pos_order_line(osv.osv):
    _inherit = "pos.order.line"

    _columns = {
        'gross_margin': fields.float('Gross Margin', digits_compute=dp.get_precision('Product Price')),
        'standard_price': fields.float('Cost Price', digits_compute=dp.get_precision('Product Price'))
    }