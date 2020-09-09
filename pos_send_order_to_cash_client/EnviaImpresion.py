# -*- encoding: utf-8 -*-
#Envia a imprimir cada 2 segundos segun cola de impresion
##Instalacion:
#-------------
#Instalar pywin32 desde https://pypi.python.org/pypi/pywin32
##Copiar en la carpeta C:\Python27\Lib\site-packages\win32 para un mejor control
#
#Si hubiese un error que no inicia el servicio, ver el log de aplicacion de Windows
import win32service
import win32serviceutil
import win32event
import time
import psycopg2
import subprocess as sp

class PySvcPrint(win32serviceutil.ServiceFramework):
    # you can NET START/STOP the service by the following name
    _svc_name_ = "PySvcPrint"
    # this text shows up as the service name in the Service
    # Control Manager (SCM)
    _svc_display_name_ = "Python Service Imprimir desde Odoo"
    # this text shows up as the description in the SCM
    _svc_description_ = "Este servicio es usado por Odoo para imprimir los comprobantes"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        # create an event to listen for stop requests on
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)

    # core logic of the service
    def SvcDoRun(self):
        # if the stop event hasn't been fired keep looping
        Cola = ProcesaCola()

        rc = None
        while rc != win32event.WAIT_OBJECT_0:
            Cola.procesa()
            # block for 5 seconds and listen for a stop event
            rc = win32event.WaitForSingleObject(self.hWaitStop, 5000)
        Cola.write_log('SHUTTING DOWN')
        Cola.desconecta()

    # called when we're being shut down
    def SvcStop(self):
        # tell the SCM we're shutting down
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        # fire the stop event
        win32event.SetEvent(self.hWaitStop)

class ProcesaCola():

    def __init__(self):
        self.conn = psycopg2.connect(database='posbox', user='openpg', password='openpgpwd', host='localhost')

    def desconecta(self):
        self.conn.close()

    def procesa(self):
        cur = self.conn.cursor()
        cur.execute("""
            select 	id, tipo_comprobante,numero,path_exe
            from	pos_comprobante_cola_impresion
            where	imprimio = false
            order by tipo_comprobante, numero
            limit 1
        """)
        rows = cur.fetchall()
        if rows:
            tipo = rows[0][1]
            numero = rows[0][2]
            path_exe = rows[0][3]
            try:
                self.write_log('Se ejecuta print_odoo.exe:' + path_exe)
                self.write_log('Se ejecuta print_odoo.exe 2:' + tipo+numero)
                sp.call([path_exe, tipo+numero])
                cur.execute("""
                    update 	pos_comprobante_cola_impresion set imprimio=true
                    where	id = %s
                """, (rows[0][1], ))
            except:
                self.write_log('Error al ejecutar print_odoo.exe:'+path_exe)
        cur.close()

    def write_log(self, msg):
        #Se guarda en la carpeta C:\Python27\Lib\site-packages\win32
        file = open('PySvcFS.log', 'a')
        file.write(time.strftime('%Y-%m-%d %H:%M:%S')+' -> '+msg+'\n')
        file.close()

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(PySvcPrint)