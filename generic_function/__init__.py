# -*- encoding: utf-8 -*-
from odoo.tools.float_utils import float_round as round
from decimal import *
import base64
from cStringIO import StringIO
from odoo.exceptions import UserError
import pytz
import os.path as path
import os
import shutil
from xml.dom import minidom
from datetime import datetime
import zipfile
import requests
import json
import tempfile

try:
    import segno
except:
    segno = None

import logging
_logger = logging.getLogger(__name__)

TWOPLACES = Decimal(10) ** -2
THREEPLACES = Decimal(10) ** -3

DAYNAMES = [(1, 'Lunes'),
            (2, 'Martes'),
            (3, 'Miercoles'),
            (4, 'Jueves'),
            (5, 'Viernes'),
            (6, 'Sabado'),
            (7, 'Domingo'),
            ]

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

def get_localize_lima_to_UTC(dt):
    if not dt:
        return False
    if type(dt) == str and len(dt) > 10:
        dt = datetime.strptime(dt, '%Y-%m-%d %H:%M:%S')
    if type(dt) == str and len(dt) == 10:
        dt = datetime.strptime(dt, '%Y-%m-%d')
    utc = pytz.utc
    lima = pytz.timezone('America/Lima')
    lima_dt = lima.localize(dt)
    utc_dt = lima_dt.astimezone(utc)
    return utc_dt

def get_localize_UTC_to_lima(dt):
    if not dt:
        return False
    if type(dt) == str and len(dt) > 10:
        dt = datetime.strptime(dt, '%Y-%m-%d %H:%M:%S')
    if type(dt) == str and len(dt) == 10:
        dt = datetime.strptime(dt, '%Y-%m-%d')
    local_tz = pytz.timezone('America/Lima')
    local_dt = dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
    local_date = local_tz.normalize(local_dt)
    return local_date

def get_current_date():
    """
    Devuelve la fecha real para lima
    @return:
    """
    loca_date = get_localize_UTC_to_lima(datetime.now())
    return loca_date.strftime('%Y-%m-%d')

def get_month_name(month):
    meses = {1: 'Enero',
             2: 'Febrero',
             3: 'Marzo',
             4: 'Abril',
             5: 'Mayo',
             6: 'Junio',
             7: 'Julio',
             8: 'Agosto',
             9: 'Setiembre',
             10: 'Octubre',
             11: 'Noviembre',
             12: 'Diciembre',
             }
    return meses[int(month)]

def get_last_day_month(date):
    """Devuelve el ultimo dia del mes"""
    from calendar import monthrange
    return date.replace(day=monthrange(date.year, date.month)[1])

def get_palote_data(data, places = 2, tipo='cab'):
    """
    Toma un lista de diccionarios y los devuelve sus valores divididos en palotes
    data = [{'dato1': valor}, {'dato2': valor}]
    """
    def get_palote(line, places = 2):
        PLACE = TWOPLACES
        if places == 3:
            PLACE = THREEPLACES
        result = ''
        for item in line:
            for y in item:
                #print 'evugor:unicode', type(item[y])
                if type(item[y]) == unicode:
                    valor = item[y].encode('utf-8', 'ignore').replace('\n', ' ')
                elif type(item[y]) == float:
                    valor = str(Decimal(item[y]).quantize(PLACE))
                else:
                    valor = str(item[y])
                result += ('|' if result else '') + valor
        return result
    if tipo == 'cab':
        data2 = get_palote(data, places)
    else:
        data2 = ''
        for row in data:
            data2 += get_palote(row) + '\n'
    return data2

def round_data(data, prec):
    """
    Toma un lista de diccionarios y los valores de tipo float los redondea
    data = [{'dato1': valor}, {'dato2': valor}]
    """
    for item in data:
        for y in item:
            if type(item[y]) == float:
                item[y] = round(item[y], prec)
    return data

def round_str(value, prec=2):
    return ("{:."+str(prec)+"f}").format(round(value, prec))

def save_ir_attachment(env, file_name, model, id, data, fields_add, delete=True):
    attach = env['ir.attachment']
    #Elimina si existe ya el archivo
    if delete:
        atach_id = attach.search([('res_model', '=', model), ('res_id', '=', id), ('name', '=', file_name)])
        atach_id.with_context({'attach_ei': True}).unlink()
    fields = {
        'name': file_name,
        'datas': data,
        'datas_fname': file_name,
        'res_model': model,
        'type': 'binary',
        'res_id': id
    }
    fields.update(fields_add)
    res_id = attach.create(fields)
    return res_id

def write_file(io, file_name, data, b64data=False):
    """
    Crea un archivo con los datos enviados
    b64data, Indica si la data enviada esta codificada en base 64
    """
    file = StringIO()
    if not io:
        file = open(file_name, 'w')
    if type(data) == unicode:
        data = data.encode('utf-8', 'ignore')
    if b64data:
        file.write(base64.b64decode(data))
    else:
        file.write(data)
    if not io:
        file.close()
    return file if io else file_name

def get_b64encode(file_path):
    if not path.exists(file_path):
        return None
    with open(file_path, 'rb') as f:
        content = base64.b64encode(f.read())
    if not content:
        raise UserError('Error al obtener los datos del archivo')
    return content

def get_b64decode(content):
    data = base64.b64decode(content)
    return data

def crea_carpeta(file_path):
    if not path.exists(file_path):
        os.makedirs(file_path)

def move_file(origen, destino):
    ruta = None
    if os.path.exists(origen):
        ruta = shutil.move(origen, destino)
    return ruta

def remove(origen):
    ruta = None
    if os.path.exists(origen):
        ruta = os.remove(origen)
    return ruta

def copy2(origen, destino):
    ruta = None
    if os.path.exists(origen):
        ruta = shutil.copy2(origen, destino)
    return ruta

def get_value_tag_xml(tag, xml_content):
    """
        Devuelve el valor de un tag de un xml
    """
    if not xml_content:
        return False
    xml_doc = minidom.parseString(xml_content)
    item = xml_doc.getElementsByTagName(tag)
    for i in item:
        return i.firstChild.nodeValue
    return False

def Numero_a_Texto(number_in, nombre_moneda):
        converted = ''

        if type(number_in) != 'str':
          number = str(number_in)
        else:
          number = number_in

        number_str=number

        def convertNumber(n):
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
                converted += '%sMILLONES ' % convertNumber(millones)

        if(miles):
            if(miles == '001'):
                converted += 'MIL '
            elif(int(miles) > 0):
                converted += '%sMIL ' % convertNumber(miles)
        if(cientos):
            if(cientos == '001'):
                converted += 'UN '
            elif(int(cientos) > 0):
                converted += '%s' % convertNumber(cientos)#SE CAMBIO: SE QUITO UN ESPACIo DESpuES DE %s

        if number_dec == "":
          number_dec = "00"
        if (len(number_dec) < 2 ):
          number_dec+='0'

        if float(number_str) >= 0 and float(number_str) < 1:
            converted = 'CERO '
        converted += 'Y '+ number_dec + "/100 " + nombre_moneda
        return converted


def format_number_to_text(number, decimal=2):
    """
    Usado para impresion de tickets en el TPV
    """
    f = '{0:.'+str(decimal)+'f}'
    num = f.format(round(number, decimal))
    return num

def texto_two_columns(val_left, val_right, width):
    """
    Usado para impresion de tickets en el TPV
    """
    space = ' ' * (width - (len(val_left) + len(val_right)))
    texto = val_left + space + val_right
    return texto

def extract_file_zip(file_zip, file_extract):
    """
    De un archivo Zip, extrae un archivo dado
    :param file_zip:
    :param file_extract:
    :return:
    """
    path_root = os.path.join(os.path.dirname(os.path.abspath(__file__)))
    zf = zipfile.ZipFile(file_zip, "r")
    file_name = zf.extract(file_extract, path_root)
    return file_name

def extract_file_zip_b64(file_base64, file_extract, b64=True):
    """
    De un archivo Zip en base64, extrae un archivo su contenido o en base64
    """
    in_memory_data = BytesIO()
    in_memory_data.write(base64.b64decode(file_base64))
    in_memory_zip = zipfile.ZipFile(in_memory_data)
    file_data = in_memory_zip.read(file_extract)
    in_memory_zip.close()
    in_memory_data.close()
    return base64.b64encode(file_data) if b64 else file_data

def request_json(url, data):
    """
    Realiza una peticion JSON
    @param url:
    @param data:
    @return: Retorna un dict si todo fue correcto, un string o exception si hubo errores
    """
    s = requests.Session()
    headers = {'Content-Type': 'application/json'}
    request_json = {'jsonrpc': '2.0',
                    'method': 'call',
                    'params': {'context': {},
                               'json_data': data
                               },
                    'id': False}
    request_json = json.dumps(request_json)
    try:
        try:
            from urllib.parse import urlparse #Python3
        except:
            from urlparse import urlparse #Python2
        url_data = urlparse(url)
        url_db = '{scheme}://{netloc}/web?db={db}'.format(scheme=url_data.scheme,
                                                         netloc=url_data.netloc,
                                                         db=url_data.netloc.split('.')[0]
                                                         )
        if url_db.find('localhost') == -1 and url_db.find(':8069') == -1:#Si no es localhost
            s.get(url_db)
        #s.get('http://localhost:8085/web?db=app-einvoice')#para prueba local
        print 'url', url
        res = s.post(url, data=request_json, headers=headers)
    except requests.exceptions.RequestException as err:
        return err
    except requests.exceptions.ConnectionError as err:
        return err
    except requests.exceptions.HTTPError as err:
        return err
    except requests.exceptions.URLRequired as err:
        return err
    except requests.exceptions.TooManyRedirects as err:
        return err
    except requests.exceptions.ConnectTimeout as err:
        return err
    except requests.exceptions.ReadTimeout as err:
        return err
    except requests.exceptions.Timeout as err:
        return err
    if res.status_code == 200:
        res_json = res.json()
        if res_json.get('error', False):
            return 'Mensaje de WebService:%s\n%s' % (url, res_json['error']['data']['message'])
    elif res.status_code == 404:
        error = 'No se encuentra la URL:%s\nstatus_code=%s' % (url, res.status_code)
        return error
    else:
        try:
            error = 'Error en la solicitud:%s\nstatus_code=%s' % (url, res.status_code)
            return error
        except:
            error = "Excepcion al crear mensaje de Error"
            _logger.exception(error)
            _logger.exception(res.status_code)
            return error
    return json.loads(res_json['result'])


def qr_code(value):
    """
    Devuelve un codigo QR segun la norma ISO/IEC 18004:2006 establecida por SUNAT.

    6.5 Código de barras QR
        6.5.1. Simbología
        Para la generación del código de barras se hará uso de la simbología QR Code 2005
        de acuerdo a la Norma ISO/IEC 18004:2006. D3enominsad “Information technology –
        Automatic identification and data capture techniques – QR Code 2005 bar code
        symbology specification”. No debe usarse las variantes:
        a) Micro QR.

        6.5.2. Características técnicas
        a) Nivel de corrección de error (Error Correction Level): nivel Q.
        b) Dimensiones mínimas de los elementos del código de barras:
            Ancho mínimo de un módulo (X-Dimension): 0,0075 pulgadas (0,190 mm).
            Codificacion de caracteres UTF8

    6.5.4 Características de la Impresión
        La impresión debe cumplir las siguientes características:
        e) Posición del código de barras dentro de la representación impresa: Parte inferior de
        la representación impresa.
        f) Tamaño máximo: 6 cm de alto y 6 cm de ancho (incluye el espacio en blanco
        alrededor del código).
        g) Zona de silencio mínimo (Quiet Zone) o ancho mínimo obligatorio en blanco
        alrededor del código impreso para delimitarlo: 1 mm.
        h) Color de impresión: Negro.
    """
    qr = segno.make_qr(value, encoding='utf-8', error='Q')
    file = tempfile.NamedTemporaryFile(suffix='.png')
    qr.save(file, scale=4)
    file.seek(0)
    image_base64 = get_b64encode(file.name)
    file.close()
    return image_base64

def convert_xls_to_csv(data):
    """
    :param data: data in format xls
    :return: data in format csv
    """
    import os
    import tempfile
    import base64
    import pandas as pd

    # Crea temporales
    fxls, xls_fname = tempfile.mkstemp()
    fcsv, csv_fname = tempfile.mkstemp(suffix='.csv')
    # Excribe los datos del archivo Excel
    os.write(fxls, base64.b64decode(data))
    os.close(fxls)
    # Converte de Excel a CSV
    pd.read_excel(xls_fname).to_csv(csv_fname, encoding="utf-8", index=False)
    # Lee el archivo CSV
    file_csv = open(csv_fname, 'r+')
    data_csv = base64.b64encode(file_csv.read())
    new_data = data_csv
    # Elimina temporales
    os.unlink(xls_fname)
    os.unlink(csv_fname)
    return new_data
