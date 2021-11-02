# -*- coding: utf-8 -*-

from odoo import http
import odoo.addons.generic_function as gf
import odoo.addons.hw_proxy.controllers.main as hw_proxy
import os.path as path
import sys
import subprocess as sp
import requests

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
_logger.warning('EVUGOR:PATH Python' + d)

class ImprimeBartender(hw_proxy.Proxy):

    @http.route('/hw_proxy/sendprintbartender', type='json', auth='none', cors='*')
    def sendprintbartender(self, data):
        """
            Recibe datos y crea el archivo txt
        """
        ####Funcionalidad de redireccionar impresion, solo debe descomentarse en las computadoras
        ##que no tengan la impresora conectada y se desea enviar a otro Odoo que si tenga la impresora conectada
        ##Este procedimiento se usó porque no se pudo compartir la impresora en red del bartender
        redirect = False
        if redirect:
            import requests
            import json
            s = requests.Session()
            headers = {'Content-Type': 'application/json'}
            request_json = {'jsonrpc': '2.0',
                            'method': 'call',
                            'params': {'context': {},
                                       'data': data
                                       },
                            'id': False}
            request_json = json.dumps(request_json)
            host = 'http://192.168.100.9:8069'#En algunos casos el usar nombre de equipo demora la impresion, tal vez por lentitud de la red
            url_host = host+'/hw_proxy/sendprintbartender'
            #s.get(host+'/web?db=posbox')#Se da por entendido que la base de datos se llama posbox
            res = s.post(url_host, data=request_json, headers=headers)
            _logger.info("Resultado de redireccionamiento")
            _logger.info(res)
            if res.status_code == 200:
                res_json = res.json()
                return res_json
            else:
                return {'error': 1, 'msg': 'Error en redireccionamiento a url %s' % url_host}
        #####
        data_to_file = ''
        productos = data[0]
        result = {'error': 0, 'msg': ''}
        for d in productos:
            for line in d[1:]:#No considera el primer item por ser para uso del banckend
                data_to_file += str(line.encode('utf-8', 'ignore')) + ';'
            data_to_file += '\n'
        data_to_file = data_to_file.rstrip('\n')
        if not data[1]['bart_data_path'] or not path.exists(data[1]['bart_data_path']):
            result['error'] = 1
            result['msg'] = 'La Ruta y el archivo con los datos de productos a imprimir no esta definida correctamente'
            return result
        else:
            bart_data_path = data[1]['bart_data_path']

        if not data[1]['bart_exe_path'] or not path.exists(data[1]['bart_exe_path']):
            result['error'] = 1
            result['msg'] = 'La Ruta del ejecutable Bartender no esta definida correctamente'
            return result
        else:
            bart_exe_path = data[1]['bart_exe_path']

        if not data[1]['bart_file_path'] or not path.exists(data[1]['bart_file_path']):
            result['error'] = 1
            result['msg'] = 'La Ruta donde del diseño de la etiqueta no está definida correctamente'
            return result
        else:
            bart_file_path = data[1]['bart_file_path']
        bartender_copias = '/C='+data[1]['bartender_copias']
        _logger.info("bart_exe_path =%s" % (bart_exe_path,))
        _logger.info("bart_data_path =%s" % (bart_data_path,))
        _logger.info("bart_file_path =%s" % (bart_file_path,))
        _logger.info("bartender_copias =%s" % (bartender_copias,))
        gf.write_file(False, bart_data_path, data_to_file)
        sp.call([bart_exe_path, '/P', bartender_copias, '/X', '/F='+bart_file_path])
        return result