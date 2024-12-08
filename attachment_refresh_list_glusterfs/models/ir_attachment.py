# -*- coding: utf-8 -*-

from odoo import fields, models, api
import base64
import os
from odoo.tools import human_size
import logging
_logger = logging.getLogger(__name__)

class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    @api.model
    def _file_read(self, fname, bin_size=False):
        """En caso de problemas de lectura de metadatos producto del uso de glusterfs, si hay error de lectura
        se procede a listar el directorio para actualizar el metadato.
        """
        full_path = self._full_path(fname)
        r = ''
        try:
            if bin_size:
                r = human_size(os.path.getsize(full_path))
            else:
                with open(full_path, 'rb') as fd:
                    r = base64.b64encode(fd.read())
        except (IOError, OSError):
            _logger.info("_read_file fallo para %s, intentando actualizar el directorio", full_path, exc_info=False)
            # Forzar una actualización de metadatos
            directory = os.path.dirname(full_path)
            try:
                _ = os.listdir(directory)  # Listar el directorio para "autocompletar"
                _logger.info("Listado de directorio para %s realizado con exito", directory)

                # Reintentar la operación
                if bin_size:
                    r = human_size(os.path.getsize(full_path))
                else:
                    with open(full_path, 'rb') as fd:
                        r = base64.b64encode(fd.read())
            except (IOError, OSError):
                _logger.error("No se pudo actualizar ni leer el archivo %s", full_path, exc_info=True)
        return r