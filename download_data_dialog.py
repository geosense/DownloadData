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

    def import_error_message(self, modules):
        """Will print error message about not imported modules
        """

        msg = QtGui.QMessageBox()
        msg.setIcon(QtGui.QMessageBox.Critical)
        msg.setText(u"Nepodařilo se načít některé důležité moduly")
        msg.setWindowTitle(u"Chyba při importu modulů")
        msg.setInformativeText(
            u"Bohužel se nepodařilo načíst některé důležité moduly:\n\n" \
            u"  {}\n\n" \
            u"Zřejmě je nemáte nainstalované ve vašem systému.\n\n" \
            u"Návod na instalaci chybějících modulů můžete nalézt " \
            u"níže:".format(", ".join(modules)))

        how_to = ''
        pip = ""
        import platform
        if platform.system() != 'Windows':
            how_to = u"Pro instalaci chybějích modulů spusťte příkazovou " \
            u"řádku Windows (cmd) a v ní spusťte následující příkaz: \n\n"
            pip = u"C:\\OSGeo4W\\apps\\Python27\\Scripts\\pip.exe"
        else:
            how_to = u"Pro instalaci chybějích modulů spusťte příkazovou " \
            u"řádku a použijte příkaz: \n\n"
            pip = "pip"

        for module in modules:
            how_to += u"  {} install {}\n".format(pip, module)

        msg.setDetailedText(how_to)

        msg.setStandardButtons(QtGui.QMessageBox.Ok)
        msg.exec_()




    def enable_output(self):
        self.outputDirButton.setEnabled(True)

    def selectdir(self):
        self.outputDir.setText(QtGui.QFileDialog.getSaveFileName(self,
                                                                  "Save Outup as *.shp",
                                                                  QtCore.QDir.homePath(),
                                                                  "shapefile (*.shp)") + ".shp")
        self.button_box.setEnabled(True)
	self.images.setEnabled(True)
        self.documents.setEnabled(True)

