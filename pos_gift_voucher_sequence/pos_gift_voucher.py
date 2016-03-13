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
    _inherit = "pos.gift.voucher"

    _defaults = {
        'gift_voucher_serial': '/',
    }

    _sql_constraints = [
        ('gift_voucher_serial_uniq', 'unique (1=1)', ''),
    ]

    def action_opened(self, cr, uid, ids, context=None):
        result = super(pos_gift_voucher, self).action_opened(cr, uid, ids, context=context)
        for gift in self.browse(cr, uid, ids, context=context):
            sequence = self.pool.get('ir.sequence').get_id(cr, uid, 'pos.gift.voucher', 'code', context=context)
            self.write(cr, uid, gift.id, {'gift_voucher_serial': sequence}, context=context)
        return result