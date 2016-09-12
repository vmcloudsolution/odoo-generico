# -*- coding: utf-8 -*-
##############################################################################
#
#    This module copyright :
#        (c) 2016 VMCloud Solution (http://vmcloudsolution.pe)
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
from openerp import tools, SUPERUSER_ID

class res_users(osv.osv):
    _inherit = 'res.users'
    _columns = {
        'pin_code': fields.char('PIN code', size=4, copy=False, help="The PIN code must be four digits"),
    }

    def _check_pin(self, cr, uid, ids, context=None):
        for obj in self.browse(cr, uid, ids, context=context):
            if obj.pin_code and not (obj.pin_code.isdigit() and len(obj.pin_code) == 4):
                return False
        return True

    _constraints = [
            (_check_pin, 'Ingrese un número valido de cuatro digitos para el código PIN del vale: Ejemplo: 1234', ['pin_code']),
        ]

    _sql_constraints = [('pin_code_uniq', 'unique (pin_code2)', 'El codigo PIN debe ser unico por usuario!')]

class pos_config(osv.osv):
    _inherit = 'pos.config'

    _columns = {
        'lockscreen_every_order': fields.boolean('Lock screen every order', help='Lock screen every POS order'),
    }