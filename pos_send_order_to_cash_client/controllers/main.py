# -*- coding: utf-8 -*-

from odoo import http
import odoo.addons.hw_proxy.controllers.main as hw_proxy
import sys
import subprocess as sp
from odoo.http import request

sys.path.append('C:\\Windows\system32\python27.zip')
sys.path.append('C:\\Python27\\DLLs')
sys.path.append('C:\\\\Python27\\lib')
sys.path.append('C:\\Python27\lib\\plat-win')
sys.path.append('C:\\Python27\lib\\lib-tk')
sys.path.append('C:\\Python27')
sys.path.append('C:\\Python27\lib\\site-packages')
sys.path.append('C:\\Python27\lib\\site-packages\\win32')
sys.path.append('C:\\Python27\lib\\site-packages\\win32\lib')
sys.path.append('C:\\Python27\lib\\site-packages\\Pythonwin')

import logging
_logger = logging.getLogger(__name__)
d = '; '.join(sys.path)

class GetCorrelativoCaja(hw_proxy.Proxy):

    # @http.route('/hw_proxy/getcorrelativo', type='json', auth='none', cors='*')
    # def getcorrelativo(self, data):
    #     res_company = request.env['res.company']
    #     res = res_company.get_num_seq(data)
    #     return res

    @http.route('/hw_proxy/verif_seq', type='json', auth='none', cors='*')
    def verif_seq(self, data, pos_reference=False, get_seq=False, vat=False):
        """Verifica la existencia de una secuencia.
        get_seq: Si es verdadero devuelve el valor de la secuencia verificada
        """
        res_company = request.env['res.company']
        res = res_company.verif_seq(data, vat)
        if res and get_seq:
            res = res_company.get_num_seq(data, pos_reference, vat)
        return res

    @http.route('/hw_proxy/grabacomprobante', type='json', auth='none', cors='*')
    def grabacomprobante(self, data):
        res_company = request.env['res.company']
        res = res_company.graba_comprobante(data)
        return res

    @http.route('/hw_proxy/grabaguia', type='json', auth='none', cors='*')
    def grabaguia(self, data):
        res_company = request.env['res.company']
        res = res_company.graba_guia(data)
        return res

    @http.route('/hw_proxy/grabainvoice', type='json', auth='none', cors='*')
    def grabainvoice(self, data):
        res_company = request.env['res.company']
        res = res_company.graba_invoice(data)
        return res

    @http.route('/hw_proxy/grabaletter', type='json', auth='none', cors='*')
    def grabaletter(self, data):
        res_company = request.env['res.company']
        res = res_company.graba_letter(data)
        return res

    @http.route('/hw_proxy/save_order', type='json', auth='none', cors='*')
    def save_order(self, data, vat=False):
        """Guarda el pedido en JSON para luego recuperarlo
        """
        pos_order_send = request.env['pos.order.send']
        res = pos_order_send.save_order(data, vat)
        return res

    @http.route('/hw_proxy/load_order_cash', type='json', auth='none', cors='*')
    def load_order_cash(self, data):
        """Recupera Todos los JSON
        """
        pos_order_send = request.env['pos.order.send']
        res = pos_order_send.load_order_cash(data)
        return res

    @http.route('/hw_proxy/process_order_cash', type='json', auth='none', cors='*')
    def process_order_cash(self, data):
        pos_order_send = request.env['pos.order.send']
        res = pos_order_send.process_order_cash(data)
        return res