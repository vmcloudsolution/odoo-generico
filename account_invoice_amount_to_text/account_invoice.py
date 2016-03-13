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

UNIDADES = (
    '',
    'UN ',
    'DOS ',
    'TRES ',
    'CUATRO ',
    'CINCO ',
    'SEIS ',
    'SIETE ',
    'OCHO ',
    'NUEVE ',
    'DIEZ ',
    'ONCE ',
    'DOCE ',
    'TRECE ',
    'CATORCE ',
    'QUINCE ',
    'DIECISEIS ',
    'DIECISIETE ',
    'DIECIOCHO ',
    'DIECINUEVE ',
    'VEINTE '
)
DECENAS = (
    'VENTI',
    'TREINTA ',
    'CUARENTA ',
    'CINCUENTA ',
    'SESENTA ',
    'SETENTA ',
    'OCHENTA ',
    'NOVENTA ',
    'CIEN '
)
CENTENAS = (
    'CIENTO ',
    'DOSCIENTOS ',
    'TRESCIENTOS ',
    'CUATROCIENTOS ',
    'QUINIENTOS ',
    'SEISCIENTOS ',
    'SETECIENTOS ',
    'OCHOCIENTOS ',
    'NOVECIENTOS '
)

class account_invoice(osv.osv):
    _inherit = "account.invoice"

    def _get_amount_text(self, cr, uid, ids, name, arg, context=None):
        result = {}
        for invoice in self.browse(cr, uid, ids, context=context):
            result[invoice.id] = self.Numero_a_Texto(invoice.amount_total, invoice.currency_id.name2 if invoice.currency_id.name2 else invoice.currency_id.name)
        return result

    _columns = {
        'amount_text': fields.function(_get_amount_text, string='Amount text', type='char'),
    }

    def Numero_a_Texto(self, number_in, nombre_moneda):
        converted = ''

        if type(number_in) != 'str':
          number = str(number_in)
        else:
          number = number_in

        number_str=number

        try:
          number_int, number_dec = number_str.split(".")
        except ValueError:
          number_int = number_str
          number_dec = ""

        number_str = number_int.zfill(9)
        millones = number_str[:3]
        miles = number_str[3:6]
        cientos = number_str[6:]

        if(millones):
            if(millones == '001'):
                converted += 'UN MILLON '
            elif(int(millones) > 0):
                converted += '%sMILLONES ' % self.__convertNumber(millones)

        if(miles):
            if(miles == '001'):
                converted += 'MIL '
            elif(int(miles) > 0):
                converted += '%sMIL ' % self.__convertNumber(miles)
        if(cientos):
            if(cientos == '001'):
                converted += 'UN '
            elif(int(cientos) > 0):
                converted += '%s' % self.__convertNumber(cientos)#SE CAMBIO: SE QUITO UN ESPACIo DESpuES DE %s

        if number_dec == "":
          number_dec = "00"
        if (len(number_dec) < 2 ):
          number_dec+='0'

        converted += 'Y '+ number_dec + "/100 " + nombre_moneda

        return converted

    def __convertNumber(self, n):
        output = ''

        if(n == '100'):
            output = "CIEN "
        elif(n[0] != '0'):
            output = CENTENAS[int(n[0])-1]

        k = int(n[1:])
        if(k <= 20):
            output += UNIDADES[k]
        else:
            if((k > 30) & (n[2] != '0')):
                output += '%sY %s' % (DECENAS[int(n[1])-2], UNIDADES[int(n[2])])
            else:
                output += '%s%s' % (DECENAS[int(n[1])-2], UNIDADES[int(n[2])])

        return output