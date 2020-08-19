# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2016 Shawn
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
{
    "name": "Multi-selection for one2many fields",
    "version": "1.0",
    "author": "VMCLOUD SOLUTION",
    "license": "AGPL-3",
    "summary": "This widget adds the capability for selecting multiple records in one2many fields",
    "description": '''
    ''',
    "category": "Web Enhancements",
    "depends": [
        'web',
    ],
    "data": [
        "view/web_assets.xml",
    ],
    "qweb":[
        'static/src/xml/widget_view.xml',
    ],
    "auto_install": False,
    "installable": True,
    "application": False,
}
