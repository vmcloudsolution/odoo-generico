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
from dateutil.relativedelta import relativedelta
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

class pos_gift_voucher(osv.osv):
    _name = "pos.gift.voucher"
    _order = "issue_date desc"

    def _expiry_date(self, cr, uid, context=None):
        date_start = datetime.now()
        date_end = date_start + relativedelta(years=1)
        date_end = date_end.strftime('%Y-%m-%d %H:%M:%S')
        return date_end

    def _validity_days(self, cr, uid, ids, name, attr, context=None):
        res = {}
        for gift in self.browse(cr, uid, ids, context=context):
            date_start = datetime.strptime(gift.issue_date, '%Y-%m-%d %H:%M:%S')
            date_end = datetime.strptime(gift.expiry_date, '%Y-%m-%d %H:%M:%S')
            diff = date_end - date_start
            if diff.days < 0:
                res[gift.id] = 0
            else:
                res[gift.id] = diff.days
        return res

    _columns = {
        'name': fields.char('Name', select=1, required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'order_id': fields.many2one('pos.order', 'Ref. Order', readonly=True, states={'draft': [('readonly', False)]}),
        'partner_id': fields.many2one('res.partner', 'Customer', readonly=True, states={'draft': [('readonly', False)]}),
        'validity': fields.function(_validity_days, type='integer', string='Validity days'),
        'issue_date': fields.datetime('Issue date', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'expiry_date': fields.datetime('Expiry date', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'amount': fields.float('Amount', digits_compute=dp.get_precision('Product Price'), readonly=True, states={'draft': [('readonly', False)]}),
        'gift_voucher_serial': fields.char('Gift voucher serial', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'total_available': fields.integer('Total available', required=True,  readonly=True, states={'draft': [('readonly', False)]}),
        'total_available_orig': fields.integer('Total available original', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'order_ids': fields.many2many('pos.order', 'pos_order_gift_voucher', 'pos_gift_voucher_id', 'pos_order_id', 'Orders', readonly=True),
        'state': fields.selection([('draft', 'Draft'),
                                   ('opened', 'In Progress'),
                                   ('cancel', 'Cancel'),
                                   ('redeemed', 'Redeemed'),
                                   ],
                                  'Status', readonly=True, copy=False),
        'user_id': fields.many2one('res.users', 'Responsable', readonly=True, states={'draft': [('readonly', False)]}),
    }

    _defaults = {
        'amount': 0,
        'issue_date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'expiry_date': _expiry_date,
        'total_available': 1,
        'state': 'draft',
    }

    _sql_constraints = [
        ('gift_voucher_serial_uniq', 'unique (gift_voucher_serial)', 'The serial of the gift voucher must be unique!'),
        ('gift_voucher_total_available', 'CHECK (total_available>=0)', 'The total available of the gift voucher must be greater or equal to zero!')
    ]

    def onchange_voucher_serial(self, cr, uid, ids, serial, context=None):
        if serial:
            v = {
                'name': 'VALE-'+serial,
            }
            return {'value': v}
        return {}

    def onchange_total_available(self, cr, uid, ids, total_available, context=None):
        if total_available:
            v = {
                'total_available_orig': total_available,
                 }
            return {'value': v}
        return {}

    def onchange_order(self, cr, uid, ids, order_id, context=None):
        if order_id:
            pos_order = self.pool.get('pos.order').browse(cr, uid, order_id, context=context)
            v = {
                'partner_id': pos_order.partner_id,
                'user_id': pos_order.user_id,
                'issue_date': pos_order.date_order,
            }
            return {'value': v}
        return {}

    def unlink(self, cr, uid, ids, context=None):
        for gift in self.browse(cr, uid, ids, context=context):
            if not gift.state == 'draft':
                raise osv.except_osv(_('Unable to Delete!'), _('To remove a gift voucher, it must be draft'))
        return super(pos_gift_voucher, self).unlink(cr, uid, ids, context=context)

    def set_redeemed(self, cr, uid, ids, context=None):
        for gift_obj in self.browse(cr, uid, ids, context=context):
            if gift_obj.total_available == 0:
                self.write(cr, uid, gift_obj.id, {'state': 'redeemed'}, context=context)
        return True

    def action_opened(self, cr, uid, ids, context=None):
        for gift in self.browse(cr, uid, ids, context=context):
            if gift.state not in 'draft':
                raise osv.except_osv(_('Operation Forbidden!'),
                                     _('Gift voucher must be in state \'Draft\''))
        self.write(cr, uid, ids, {'state': 'opened'}, context=context)
        return True

    def action_cancel(self, cr, uid, ids, context=None):
        """ Cancel the Gift Voucher
        :return: True
        """
        for gift in self.browse(cr, uid, ids, context=context):
            if gift.state == 'redeemed':
                raise osv.except_osv(_('Operation Forbidden!'),
                                     _('You cannot cancel a gift voucher that has been set to \'Redeemed\'.'))
        self.write(cr, uid, ids, {'state': 'cancel'}, context=context)
        return True

    def action_opened_to_draft(self, cr, uid, ids, context=None):
        """ Change state opened to draft
        """
        for gift in self.browse(cr, uid, ids, context=context):
            if gift.order_ids:
                raise osv.except_osv(_('Operation Forbidden!'),
                                     _('You cannot change to Draft a gift voucher that has orders.'))
        self.write(cr, uid, ids, {'state': 'draft'}, context=context)
        return True

    def get_voucher_ids(self, cr, uid, gift_voucher_serial, context=None):
        voucher_ids = self.search(cr, uid, [('gift_voucher_serial', '=', gift_voucher_serial),
                                            ('state', '=', 'opened'),
                                            ('expiry_date', '>=', time.strftime('%Y-%m-%d %H:%M:%S')),
                                            ], context=context)
        return voucher_ids

    def get_voucher_amount(self, cr, uid, partner_id, gift_voucher_serial, context=None):
        """
            if spent is 0 gift voucher is not valid.
        """
        voucher_amount = 0
        voucher_spent = 0
        mensaje_error = ''
        voucher_ids = self.get_voucher_ids(cr, uid, gift_voucher_serial, context=context)
        for gift_voucher in self.browse(cr, uid, voucher_ids, context=context):
            if gift_voucher.partner_id and gift_voucher.partner_id != partner_id:
                continue
            voucher_amount = gift_voucher.amount
            voucher_spent = 1
        result = [voucher_amount, voucher_spent, mensaje_error]
        return result