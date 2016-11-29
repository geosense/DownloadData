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
        # widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

        self.treeWidget.clicked.connect(self.enable_output)
        self.outputDirButton.clicked.connect(self.selectdir)

    def import_error_message(self, modules):
        """Will print error message about not imported modules
        """

        msg = QtGui.QMessageBox()
        msg.setIcon(QtGui.QMessageBox.Critical)
        msg.setText(self.tr("Nepodařilo se načít některé důležité moduly"))
        msg.setWindowTitle(self.tr("Chyba při importu modulů"))
        msg.setInformativeText(self.tr(
            "Bohužel se nepodařilo načíst některé důležité moduly:\n\n"
            "  {}\n\n"
            "Zřejmě je nemáte nainstalované ve vašem systému.\n\n"
            "Návod na instalaci chybějících modulů můžete nalézt "
            "níže:").format(", ".join(modules)))

        how_to = ''
        pip = ""
        import platform
        if platform.system() == 'Windows':
            how_to = self.tr("Pro instalaci chybějích modulů spusťte příkazovou "
                             "řádku Windows (cmd) a v ní spusťte následující příkaz: \n\n")
            pip = "C:\\OSGeo4W\\apps\\Python27\\Scripts\\pip.exe"
        else:
            how_to = self.tr("Pro instalaci chybějích modulů spusťte příkazovou "
                             "řádku a použijte příkaz: \n\n")
            pip = "pip"

        for module in modules:
            how_to += "  {} install {}\n".format(pip, module)

        msg.setDetailedText(how_to)

        msg.setStandardButtons(QtGui.QMessageBox.Ok)
        msg.exec_()

    def enable_output(self):
        self.outputDirButton.setEnabled(True)

    def selectdir(self):
        self.outputDir.setText(QtGui.QFileDialog.getExistingDirectory(self,
                                                                 self.tr(
                                                                 "Save Output to"),
                                                                 QtCore.QDir.homePath()))
        self.images.setEnabled(True)
        self.documents.setEnabled(True)
        self.button_box.setEnabled(True)

    def show(self):

        # domains
        self.domain.clear()
        self.domain.setEnabled(True)
        domains = ['cz', 'sk', 'com']
        self.domain.addItems(domains)

        self.getData.setEnabled(True)
        self.maName.setEnabled(True)
        self.checkBox.setEnabled(True)
        self.checkBox.setChecked(True)
        self.userName.setDisabled(True)
        self.userPassword.setDisabled(True)
        self.button_box.setDisabled(True)
        self.outputDir.setDisabled(True)
        self.outputDir.clear()
        self.outputDirButton.setDisabled(True)
        self.treeWidget.clear()
        self.treeWidget.setDisabled(True)
        self.images.setDisabled(True)
        self.images.setChecked(False)
        self.documents.setDisabled(True)
        self.documents.setChecked(False)

        return super(DownloadDataDialog, self)
