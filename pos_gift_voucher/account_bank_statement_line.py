# -*- coding: utf-8 -*-
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

class account_bank_statement_line(osv.osv):
    _inherit = 'account.bank.statement.line'

    _columns = {
        'gift_voucher_id': fields.many2one('pos.gift.voucher', 'Gift Voucher', readonly=True),
        'amount_gift': fields.float('Amount vale', digits_compute=dp.get_precision('Product Price'), readonly=True),
        'total_gift': fields.integer('Total ', readonly=True, ),
    }