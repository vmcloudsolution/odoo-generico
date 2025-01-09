# -*- coding: utf-8 -*-

from odoo import fields, models, api
import os
import logging
_logger = logging.getLogger(__name__)

class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    @api.model
    def _file_read(self, fname, bin_size=False):
        """
        Igual que _record_to_stream en lineas arriba
        """
        self.check_file_to_read()
        return super(IrAttachment, self)._file_read(fname, bin_size)

    def check_file_to_read(self):
        for attch in self:
            full_path = attch._full_path(attch.store_fname)
            print('checkkkk', full_path)
            if not os.path.exists(full_path):
                _logger.info("Archivo que se intenta leer no existe %s. Intentando actualizar el directorio", full_path,
                             exc_info=False)
                try:
                    # Forzar una actualización de metadatos
                    directory = os.path.dirname(full_path)
                    _ = os.listdir(directory)  # Listar el directorio para "autocompletar"
                    _logger.info("Listado de directorio para %s realizado con exito", directory)
                except (IOError, OSError):
                    _logger.error("No se pudo actualizar ni leer el archivo %s", full_path, exc_info=True)