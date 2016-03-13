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

from datetime import datetime
import time
from openerp.osv import fields, osv

class pos_gift_voucher(osv.osv):
    _inherit = "pos.gift.voucher"

    def export_for_printing(self, cr, uid, voucher_ids, context=None):
        receipts = []
        posbox_proxy_device_obj = self.pool.get('posbox.proxy.backend')
        obj_precision = self.pool.get('decimal.precision')
        dp = obj_precision.precision_get(cr, uid, 'Product Price')
        date_format = posbox_proxy_device_obj.get_date_formats(cr, uid, context=context)
        current_date = fields.datetime.context_timestamp(cr, uid, datetime.now(), context=context).strftime(date_format[0] + ' ' + date_format[1])
        for voucher_id in voucher_ids:
            voucher_obj = self.browse(cr, uid, voucher_id, context=context)
            receipt = {
                'name': voucher_obj.name,
                'issue_date': fields.datetime.context_timestamp(cr, uid, datetime.strptime(voucher_obj.issue_date, '%Y-%m-%d %H:%M:%S'), context=context).strftime(date_format[0] + ' ' + date_format[1]),
                'expiry_date': fields.datetime.context_timestamp(cr, uid, datetime.strptime(voucher_obj.expiry_date, '%Y-%m-%d %H:%M:%S'), context=context).strftime(date_format[0] + ' ' + date_format[1]),
                'gift_voucher_serial': voucher_obj.gift_voucher_serial,
                'company': {
                    'name': voucher_obj.create_uid.company_id.name,
                    'company_registry': voucher_obj.create_uid.company_id.company_registry,
                    'website': voucher_obj.create_uid.company_id.website,
                    'email': voucher_obj.create_uid.company_id.email,
                    'street': voucher_obj.create_uid.company_id.street,
                },
                'salesman': voucher_obj.create_uid.partner_id.name,
                'amount': round(voucher_obj.amount, dp),
                'print_date': current_date,
            }
            receipts.append(receipt)
        return receipts