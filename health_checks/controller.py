# -*- coding: utf-8 -*-
from odoo import http

class VerificaSaludServer(http.Controller):
    @http.route('/verifica_salud', type='http', auth="none", save_session=False)
    def verifica_salud(self, **kw):
        """
        Se crea endpoint para verificar salud mediante http, esto es usado por tengine nginx o un balanceador de carga
        """
        return http.Response(status=200)