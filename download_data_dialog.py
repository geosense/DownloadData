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
import qgis.utils


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

        domains = ['cz', 'sk', 'com']
        self.domain.addItems(domains)

        self.treeWidget.clicked.connect(self.enable_output)
        self.outputDirButton.clicked.connect(self.selectdir)

        self.button_box.helpRequested.connect(self.show_help)
        self.button_box.button(QtGui.QDialogButtonBox.Reset).clicked.connect(self.reset)

    def import_error_message(self, modules):
        """Will display error message about not imported modules
        """

        msg = QtGui.QMessageBox()
        msg.setIcon(QtGui.QMessageBox.Critical)
        msg.setText(self.tr("Could not load some of important modules"))
        msg.setWindowTitle(self.tr("Error while loading modules"))
        msg.setInformativeText(self.tr(
            "Some of important modules could not be loaded:\n\n"
            "  {}\n\n"
            "It seems, they are not available in your Python instance.\n\n"
            "You can find a manual how to install Python modules lower: "
            ).format(", ".join(modules)))

        how_to = ''
        pip = ""
        import platform
        if platform.system() == 'Windows':
            how_to = self.tr("For installation of missing modules, open Windows "
                             "command line (cmd) and run following command: \n\n")
            pip = "C:\\OSGeo4W\\apps\\Python27\\Scripts\\pip.exe"
        else:
            how_to = self.tr("For installation of missing modules, open Terminal "
                        "emulator a and run following command: \n\n")
            pip = "pip"

        for module in modules:
            how_to += "  {} install {}\n".format(pip, module)

        msg.setDetailedText(how_to)

        msg.setStandardButtons(QtGui.QMessageBox.Ok | QtGui.QMessageBox.Help)
        msg.button(QtGui.QMessageBox.Help).clicked.connect(self.show_help)
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

    def clear(self):
        self.outputDir.clear()
        self.treeWidget.clear()
        self.outputFile.clear()
        self.images.setChecked(False)
        self.documents.setChecked(False)

    def show(self):

        # domains
        self.domain.setEnabled(True)
        self.getData.setEnabled(True)
        self.maName.setEnabled(True)
        self.checkBox.setEnabled(True)
        self.checkBox.setChecked(True)
        self.userName.setDisabled(True)
        self.userPassword.setDisabled(True)

        return super(DownloadDataDialog, self)

    def show_help(self):
        qgis.utils.showPluginHelp(filename='help/build/html/index')

    def reset(self):
        self.clear()
