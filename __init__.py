# -*- coding: utf-8 -*-
"""
/***************************************************************************
 DownloadData
                                 A QGIS plugin
 get MA available data into shapefile
                             -------------------
        begin                : 2016-07-08
        copyright            : (C) 2016 by CLEERIO
        email                : alzbeta.gardonova@cleerio.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load DownloadData class from file DownloadData.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .download_data import DownloadData
    return DownloadData(iface)
