# -*- coding: utf-8 -*-
"""
/***************************************************************************
 DownloadDataDialog
                                 A QGIS plugin
 get MA available data into shapefile
                             -------------------
        begin                : 2016-07-08
        git sha              : $Format:%H$
        copyright            : (C) 2016 by CLEERIO
        email                : alzbeta.gardonova@cleerio.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os

from PyQt4 import QtGui, uic, QtCore

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'download_data_dialog_base.ui'))


class DownloadDataDialog(QtGui.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(DownloadDataDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

	self.treeWidget.clicked.connect(self.enable_output)
        self.outputDirButton.clicked.connect(self.selectdir)

    def enable_output(self):
        self.outputDirButton.setEnabled(True)

    def selectdir(self):
        self.outputDir.setText(QtGui.QFileDialog.getSaveFileName(self,
                                                                  "Save Outup as *.shp",
                                                                  QtCore.QDir.homePath(),
                                                                  "shapefile (*.shp)") + ".shp")
        self.button_box.setEnabled(True)
<<<<<<< HEAD
	self.images.setEnabled(True)
        self.documents.setEnabled(True)
=======
>>>>>>> origin/master

