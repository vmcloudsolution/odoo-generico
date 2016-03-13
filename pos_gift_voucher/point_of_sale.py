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

import time
from openerp.osv import fields, osv
from openerp.tools.translate import _


class pos_order(osv.osv):
    _name = 'pos.order'
    _inherit = 'pos.order'

    def _payment_fields(self, cr, uid, ui_paymentline, context=None):
        res = super(pos_order, self)._payment_fields(cr, uid, ui_paymentline, context=context)
        res['gift_voucher_serial'] = ui_paymentline.get('gift_voucher_serial', False) or ''
        res['gift_voucher_validate'] = ui_paymentline.get('gift_voucher_validate', False) or False
        return res

    def add_payment(self, cr, uid, order_id, data, context=None):
        res = super(pos_order, self).add_payment(cr, uid, order_id, data, context=context)
        if data.get('gift_voucher_validate', False):
            gift_id = self.pool.get('pos.gift.voucher').search(cr, uid, [('gift_voucher_serial', '=', data.get('gift_voucher_serial')),
                                                                         ('state', '=', 'opened'),
                                                                         ('expiry_date', '>=', time.strftime('%Y-%m-%d %H:%M:%S')),
                                                                         ])
            if not gift_id:
                raise osv.except_osv('Error', _('The gift voucher:') + data.get('gift_voucher_serial') + _(' is invalid or has already redeemed.'))
            self.pool.get('account.bank.statement.line').write(cr, uid, res, {'gift_voucher_id': gift_id[0] if gift_id else 0})
            gift_obj = self.pool.get('pos.gift.voucher').browse(cr, uid, gift_id, context=context)
            self.pool.get('pos.gift.voucher').write(cr, uid, gift_id, {'total_available': gift_obj.total_available-1,
                                                                       'order_ids': [(4, order_id)],
                                                                       })
            self.pool.get('pos.gift.voucher').set_redeemed(cr, uid, gift_id, context=context)
        return res