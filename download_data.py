# -*- coding: utf-8 -*-
"""
/***************************************************************************
 DownloadData
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
from PyQt4.QtCore import *
from PyQt4.QtCore import pyqtSlot
from qgis.core import *
from PyQt4.QtGui import QAction, QIcon, QMessageBox, QTreeWidgetItem, QProgressBar
import resources
from PyQt4 import QtCore, QtGui
import os.path
import json
import pip
#import requests
from qgis.gui import QgsMessageBar
COMBINATIONS = []
from download_data_dialog import DownloadDataDialog
import tempfile
import sqlite3
import unicodedata
import time

def install_and_import(package):
    import importlib
    try:
        importlib.import_module(package)
    except ImportError:
        import pip
        pip.main(['install', package])
    finally:
        globals()[package] = importlib.import_module(package)


install_and_import('requests')

class DownloadData:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'DownloadData_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = DownloadDataDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Download data from CLEERIO MA')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'DownloadData')
        self.toolbar.setObjectName(u'DownloadData')

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('DownloadData', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/DownloadData/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Download data from MA'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Download data from CLEERIO MA'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    def set_domains(self):
        self.dlg.domain.clear()
        self.dlg.domain.setEnabled(True)
        domains = ['geosense.cz', 'geosense.sk', 'cleerio.com']        
        self.dlg.domain.addItems(domains)

    def create_output_dir(self):
        cleerio_dir = os.path.normpath(os.path.join(QgsApplication.qgisSettingsDirPath(),'CLEERIO_data'))
        if not os.path.exists(cleerio_dir):
            os.mkdir(cleerio_dir)
        output_dir_cleerio = tempfile.mkdtemp(suffix='', prefix='download_data_',dir = cleerio_dir)
        if self.dlg.images.isChecked():
            images_dir = os.path.join(output_dir_cleerio, "images")
            os.mkdir(images_dir)
        if self.dlg.documents.isChecked():
            documents_dir = os.path.join(output_dir_cleerio, "documents")
            os.mkdir(documents_dir)


        return output_dir_cleerio
    
    def write_info(self, properties, output_dir_cleerio):
        text_file = open(os.path.join(output_dir_cleerio,'LOG_MESSAGE.txt'), "w")
        text_file.write("Atributy dat:")
        for property in properties:
            property_def = '\n' + properties[property]['label'] + ' = ' + properties[property]['name']
            text_file.write(property_def)
        text_file.close()
    
    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.set_domains()
        self.dlg.getData.setEnabled(True)
        self.dlg.maName.setEnabled(True)
        self.dlg.checkBox.setEnabled(True)
        self.dlg.checkBox.setChecked(True)
        self.dlg.userName.setDisabled(True)
        self.dlg.userPassword.setDisabled(True)
        self.dlg.button_box.setDisabled(True)
        self.dlg.outputDir.setDisabled(True)
        self.dlg.outputDir.clear()
        self.dlg.outputDirButton.setDisabled(True)
        self.dlg.treeWidget.clear()
        self.dlg.treeWidget.setDisabled(True)
        self.dlg.images.setDisabled(True)
        self.dlg.images.setChecked(False)
        self.dlg.documents.setDisabled(True)
        self.dlg.documents.setChecked(False)

        self.dlg.show()
        
        try:
            self.dlg.getData.clicked.connect(lambda: set_objects(self))
        except Exception, e:
            raise
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            progressMessageBar = self.iface.messageBar().createMessage("Zpracovávám objekty".decode('utf-8'))
            progress = QProgressBar()
            progress.setMaximum(100)
            progress.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
            progressMessageBar.layout().addWidget(progress)
            self.iface.messageBar().pushWidget(progressMessageBar, self.iface.messageBar().INFO)
            progress.setValue(2)

            selected_item = self.dlg.treeWidget.selectedItems()
            selected_layer = selected_item[0].text(0)
            
            output_dir_cleerio = self.create_output_dir()
            (obj_id, layer_id, crs) = get_object_layer_id_crs(selected_layer)

            (properties,relation_ids,relations_ids, image_ids, document_ids, link_ids, iframe_ids, id_list_ids, id_list_values) = sort_attributes(obj_id)

            data_raw = get_object_type_data(layer_id, obj_id, self.dlg.domain.currentText()) 
            
            json_no_crs = byteify(json.loads(data_raw.text, encoding="utf-8"))  

            json_crs = add_crs_definition(json_no_crs, crs )
            
            
            full_json = change_attributes(self, json_crs, properties, relation_ids,relations_ids, image_ids, document_ids, link_ids, iframe_ids, id_list_ids, id_list_values, output_dir_cleerio, progress)
            export_file = self.dlg.outputDir.text()

            geojson_path = os.path.join(output_dir_cleerio,'downloaded_data.json')
                            
            with open(geojson_path, 'w') as outfile:
                json.dump(full_json, outfile)
       
            vlayer = QgsVectorLayer(geojson_path,"mygeojson","ogr")
            _writer = QgsVectorFileWriter.writeAsVectorFormat(vlayer,export_file,"utf-8",None,"ESRI Shapefile")       
            
            shplayer = QgsVectorLayer(export_file, os.path.splitext(os.path.basename(export_file))[0], "ogr")
            QgsMapLayerRegistry.instance().addMapLayer(shplayer)
            db_name = os.path.join(output_dir_cleerio, "cleerio_data")
            QgsVectorFileWriter.writeAsVectorFormat( vlayer,
                                                 db_name,
                                                 "utf-8",
                                                 None,
                                                 'SQLite',
                                                 False,
                                                 None,
                                                 ["SPATIALITE=YES",] )
            progress.setValue(100)
            sqlitelayer =  QgsVectorLayer(db_name+".sqlite", "sqlite_vrtstva", "ogr") 
            QgsMapLayerRegistry.instance().addMapLayer(sqlitelayer)


            self.write_info(properties,output_dir_cleerio)
            self.iface.messageBar().clearWidgets() 
            text_msg = ("Stahování proběhlo, podrobná data jsou ve složce \n%s").decode("utf-8") %output_dir_cleerio
            msgBox = QMessageBox()
            msgBox.setText(text_msg)
            msgBox.setIcon(QMessageBox.Information)
            msgBox.exec_()

            pass

def download_files(file_type ,url, id_name,output_dir):
    images_dir = os.path.join(output_dir, file_type)
    if id_name != 'NULL':
        r = requests.get(url)
        output_dir
        name = os.path.join(images_dir,id_name)
        with open(name, "wb") as code:
            code.write(r.content)   

def clean_output_dir(output_dir):
    if not os.listdir(os.path.join(output_dir,'images')):
        os.rmdir(os.path.join(output_dir,'images'))
    if not os.listdir(os.path.join(output_dir,'documents')):
        os.rmdir(os.path.join(output_dir,'documents'))

def add_crs_definition(json, crs_def):
    crs = {}
    crs["type"] = "name"
    crs_properties = {}
    crs_properties["name"] = crs_def
    crs["properties"] = crs_properties
    json["crs"] = crs
    return json

def change_attributes(self, input_json, properties, relation_ids, relations_ids, image_ids, document_ids, link_ids, iframe_ids, id_list_ids, id_list_values, output_dir, progress):

    feature_count = len(input_json['features'])
    counter = 0
    for feature in input_json['features']:
        for prop_id in feature['properties'].keys():
            if prop_id not in ('layers', 'label','id', 'object_type_id'):
                prop_name = properties[prop_id]['name'] 
                value = ''
                if int(prop_id) in relation_ids and feature['properties'][prop_id] is not None:
                    value = feature['properties'][prop_id]['id']
                elif int(prop_id) in relations_ids and feature['properties'][prop_id] is not None:
                    related = []
                    for rel_object in feature['properties'][prop_id]['objects']:
                        related.append(rel_object['id'])
                    value = str(related) 
                elif int(prop_id) in image_ids and feature['properties'][prop_id] is not None:
                    value = feature['properties'][prop_id]['src']
                    if self.dlg.images.isChecked():
                        download_files('images', value, feature['properties'][prop_id]['id'], output_dir)
                elif int(prop_id) in document_ids and feature['properties'][prop_id] is not None:
                    value = feature['properties'][prop_id]['src']
                    if self.dlg.documents.isChecked():
                        download_files('documents', value,feature['properties'][prop_id]['id'], output_dir)
                elif int(prop_id) in link_ids and feature['properties'][prop_id] is not None:
                    value = feature['properties'][prop_id]['link']
                elif int(prop_id) in iframe_ids and feature['properties'][prop_id] is not None:
                    value = feature['properties'][prop_id]['src']
                elif int(prop_id) in id_list_ids and feature['properties'][prop_id] is not None:
                    value = id_list_values[feature['properties'][prop_id]]
                else:
                    value = feature['properties'][prop_id]                            
                input_json['features'][counter]['properties'][prop_name] = value                      
                del input_json['features'][counter]['properties'][prop_id]
            elif prop_id in ('label', 'object_type_id', 'layers'):
                del input_json['features'][counter]['properties'][prop_id]
        counter += 1
        progress.setValue(int((counter/float(feature_count))*96+2))

    if self.dlg.images.isChecked() or self.dlg.documents.isChecked():
        clean_output_dir(output_dir)
    return input_json


def sort_attributes(object_id):
    properties = {}
    relation_ids = []
    relations_ids = []
    image_ids = []
    document_ids = []
    link_ids = []
    iframe_ids = []
    id_list_ids = []
    id_list_values = {}
    for object_type in LAYERS_AVAILABLE['result']['objectTypes']:
        if object_type['id'] == object_id:
            for prop in object_type['controlers']:
                propert = {}
                propert['name'] = prop['name']
                propert['type'] = prop['data_type']
                propert['label'] = prop['label']
                properties[str(prop['id'])] = propert
                if prop['data_type']  == 'relation':
                    relation_ids.append(prop['id'])
                elif prop['data_type'] == 'relations':
                    relations_ids.append(prop['id'])
                elif prop['data_type'] == 'image':
                    image_ids.append(prop['id'])
                elif prop['data_type'] == 'document':
                    document_ids.append(prop['id'])
                elif prop['data_type'] == 'link':
                    link_ids.append(prop['id'])
                elif prop['data_type'] == 'iframe':
                    iframe_ids.append(prop['id'])
                elif prop['data_type'] in ('id_list', 'id_alist', 'id_elist'):
                    id_list_ids.append(prop['id'])
                    for item in prop['items']:                        
                        id_list_values[item['value']] = item['label']

    return(properties, relation_ids, relations_ids, image_ids, document_ids, link_ids, iframe_ids, id_list_ids, id_list_values)

        
def get_object_layer_id_crs(selected_layer):
    obj_id = int
    layer_id = int
    crs = None
    for layer_object in COMBINATIONS:
        if layer_object['name'] == selected_layer:
            obj_id = layer_object['object_type_id']
            layer_id = layer_object['layer_id']
            crs = layer_object['crs']
    return (obj_id, layer_id, crs)   



def set_objects(self):
    print     
    environment = get_input_variables(self, self.dlg.domain.currentText()
)
    try:
        vysledek = environment['result']
    except Exception, e:
        exc = Exception
        return exc     
    self.dlg.domain.setDisabled(True)
    self.dlg.getData.setDisabled(True)
    self.dlg.maName.setDisabled(True)
    self.dlg.checkBox.setDisabled(True)
    self.dlg.userName.setDisabled(True)
    self.dlg.userPassword.setDisabled(True)
    self.dlg.treeWidget.clear()

    global LAYERS_AVAILABLE
    LAYERS_AVAILABLE = get_user_data(self.dlg.domain.currentText())
    for layer in LAYERS_AVAILABLE['result']['layers']:
        if layer['type'] in('unip','htable'):
            layer_object_types = layer['object_type_ids']
                    
            for object_type in LAYERS_AVAILABLE['result']['objectTypes']:
                if object_type['id'] in layer_object_types:
                    new_comb = {}
                    new_comb['name'] =  (layer['name']).decode("utf-8") + ' - ' +  (object_type['name']).decode("utf-8")                        
                    new_comb['layer_id'] = layer['id']
                    layer_item = QtGui.QTreeWidgetItem([new_comb["name"]])
                    self.dlg.treeWidget.addTopLevelItem(layer_item)
                    new_comb['object_type_id'] = object_type['id']
                    new_comb['crs'] = layer['projection']
                    COMBINATIONS.append(new_comb)

    self.dlg.treeWidget.setEnabled(True)
    self.dlg.outputDir.setEnabled(True)

def get_input_variables(self, domain):
    global NAME 
    global NO_LOGIN
    global USER
    global PASSWORD
    global GP_ID
    global SESSION

    NAME = self.dlg.maName.text()
    USER = self.dlg.userName.text()
    PASSWORD = self.dlg.userPassword.text()
    NO_LOGIN = self.dlg.checkBox.isChecked()
    SESSION = requests.session()

    env_data = get_environment_data(domain)

    try:
        GP_ID = env_data['result'] ['gpId'] 
    except Exception,e:
        text_msg = ("MA '" + NAME +"' nenalezena!").decode("utf-8")
        msgBox = QMessageBox()
        msgBox.setText(text_msg)
        msgBox.setIcon(QMessageBox.Question)
        msgBox.exec_()
        exc = Exception
        return exc
    if NO_LOGIN == False:
        login_data = try_user_login(domain)
        try:
            login_status = login_data['result']
        except Exception,e:
            text_msg = ("Špatné přihlašovací údaje").decode("utf-8")
            msgBox = QMessageBox()
            msgBox.setText(text_msg)
            msgBox.setIcon(QMessageBox.Question)
            msgBox.exec_()
            exc = Exception
            return exc
    return env_data


def get_environment_data(domain):
    """
    Get infromation abour MA 
    """
    url_text = 'http://api.' + domain +'/gp2/get-environment/' + NAME
    result = SESSION.post(url_text)
    response = byteify(json.loads(result.text, encoding="utf-8"))

    try:
        test_result = response['result']
    except Exception,e:
        exc = Exception
        return exc

    return response

def try_user_login(domain):
    login = 'http://api.' + domain + '/gp2/sign-in/' + str(GP_ID)
    login_data = '{"username":"%s","password":"%s"}' %(USER,PASSWORD)

    log_in = SESSION.post(login,data=login_data)
    response = byteify(json.loads(log_in.text, encoding="utf-8"))
    
    try:
        login_status = response['result']
    except Exception,e:
        exc = Exception
        return exc
    return  response

def get_user_data(domain):
    """
    Get list of layer and object types  with read right to user
    """
    service_url = 'http://api.' + domain + '/gp2/get-environment/' + NAME
    login_data = '{"username":"%s","password":"%s"}' %(USER,PASSWORD)
    
    response_file = SESSION.post(service_url)

    response = byteify(json.loads(response_file.text, encoding="utf-8"))

    return response


def get_object_type_data(layer_id, object_type_id, domain):
    """
    Get GEOJSON by GP_ID, LAYER_ID and OBJECT_TYPE_ID
    """
    url_text = 'http://api.' + domain + '/gp2/filter-objects/' + str(GP_ID)
    data_params = """{"controlers":[],"ids_only":0,"layer_ids":[%s],
                     "object_type_ids":[%s],"paging":null,"geometries":[],
                     "order":[]}""" %(layer_id, object_type_id)       
    #url = 'http://api.' + domain + '/gp2/sign-in/' + str(GP_ID)
    #logout = 'http://api.' + domain + '/admin/default/logout?gpId=%s#' %GP_ID
    #login_data = '{"username":"%s","password":"%s"}' %(USER,PASSWORD)

    s = SESSION.post(url_text,data_params)
    
    return s


def byteify(input):

    if isinstance(input, dict):
        return {byteify(key): byteify(value)
                for key, value in input.iteritems()}
    elif isinstance(input, list):
        return [byteify(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input

