# -*- encoding: utf-8 -*-
#Crea un servicio en Windows que busca archivos en una ruta cada 5 segundos
#Lee un archivo .txt y envia la data al servidor Odoo con facturador Sunat
##Instalacion:
#-------------
#Instalar pywin32 desde https://pypi.python.org/pypi/pywin32
##Copiar en la carpeta C:\Python27\Lib\site-packages\win32 para un mejor control
#Ejecutar el archivo con el parametro install: python.exe SendFileWserviceFS.py install
#
#Si hubiese un error que no inicia el servicio, ver el log de aplicacion de Windows
import win32service
import win32serviceutil
import win32event
from glob import glob
import time
import os
import shutil
import os.path as path
import base64
import xmlrpclib
import socket

DATA_PATH = 'C:\\sunat_archivos\\sfs\\DATA_TXT\\'
PATH_ENVIO = DATA_PATH+'\\ENVIO\\'
ODOO_SERVER = 'http://192.168.2.9:8075'
DB = 'basedatos'

def get_b64encode(file_path):
    if not path.exists(file_path):
        return None
    with open(file_path, 'rb') as f:
        content = base64.b64encode(f.read().decode('ISO-8859-1').encode('utf-8'))
        f.close()
    if not content:
        raise False
    return content


class PySvcFS(win32serviceutil.ServiceFramework):
    # you can NET START/STOP the service by the following name
    _svc_name_ = "PySvcFS"
    # this text shows up as the service name in the Service
    # Control Manager (SCM)
    _svc_display_name_ = "Python Service FS"
    # this text shows up as the description in the SCM
    _svc_description_ = "Este servicio es usado por el Facturador Sunat"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        # create an event to listen for stop requests on
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)

    # core logic of the service
    def SvcDoRun(self):
        # if the stop event hasn't been fired keep looping
        Read = Readfiles()

        rc = None
        while rc != win32event.WAIT_OBJECT_0:
            Read.procesa()
            # block for 5 seconds and listen for a stop event
            rc = win32event.WaitForSingleObject(self.hWaitStop, 5000)
        Read.write_log('SHUTTING DOWN')

    # called when we're being shut down
    def SvcStop(self):
        # tell the SCM we're shutting down
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        # fire the stop event
        win32event.SetEvent(self.hWaitStop)

class OdooCn(object):
    """
    Realiza conexion via xmlrpclib con el servidor principal y envia los datos
    """
    def __init__(self, server, db=None, user=None, password=None):
        self._db = db
        self._user = user
        self._password = password
        if not server or not db or not user or not password:
            raise 'Ingrese los datos de autenticacion'
        self._common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(server))
        socket.setdefaulttimeout(10)
        self._common.version()        
        self._models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(server))
        
    def auth(self):
        self._uid = self._common.authenticate(self._db, self._user, self._password, {})
        if not self._uid:
            return False
        return True

    def send_data(self, data):
        result = self._models.execute_kw(self._db, self._uid, self._password,
                                    'fs.files.abstract', 'fs_get_files', [data])
        return result
    
class Readfiles():
    def procesa(self):
        data = {
            'files_cab': [],
            'files_det': [],
        }
        try:
            files_cab = glob('{}\\*.CAB'.format(DATA_PATH))
            files_det = glob('{}\\*.DET'.format(DATA_PATH))
        except:
            self.write_log('Error al leer archivos')
            return False
        if not files_cab or not files_det:
            return True
        for file in files_cab:
            content = get_b64encode(file)
            if not content:
                self.write_log('Error obtener base64 content cab')
                return False
            data['files_cab'].append(
                {
                    'name': os.path.basename(file),
                    'content': content
                 }
            )
        for file in files_det:
            content = get_b64encode(file)
            if not content:
                self.write_log('Error obtener base64 content det')
                return False
            data['files_det'].append(
                {
                    'name': os.path.basename(file),
                    'content': content
                }
            )
        try:
            odoo = OdooCn(server=ODOO_SERVER, db=DB, user='user', password='password')
            if not odoo.auth():
                self.write_log('Error de autenticacion')
                return False
        except Exception, e:
            self.write_log('Error al conectarse a Odoo:'+ e.message)
            return False
        # Mueve los archivos
        if not os.path.isdir(PATH_ENVIO):
            os.mkdir(PATH_ENVIO)

        def move_file(src, dst):
            if os.path.exists(dst):
                os.remove(dst)
            shutil.move(src, dst)
        for file in files_cab + files_det:
            file_dest = PATH_ENVIO + os.path.basename(file)
            move_file(file, file_dest)
        #Envia la data
        try:
            self.write_log('Enviando datos...')
            res = odoo.send_data(data)
            if type(res) == str:
                self.write_log('Error del Sistema:' + res)
        except Exception, e:
            self.write_log('Error al enviar los datos al servidor. Verifique el Log del Servidor: ' + e.message)
            return False
        return True

    def write_log(self, msg):
        #Se guarda en la carpeta C:\Python27\Lib\site-packages\win32
        file = open('PySvcFS.log', 'a')
        file.write(time.strftime('%Y-%m-%d %H:%M:%S')+' -> '+msg+'\n')
        file.close()

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(PySvcFS)