'''
NAME
FBX Meshes Batch Export

DESCRIPTION
Exports all selected meshes as individual FBX files with file name corresponding to object name.

v1.0
Created on December 18, 2020
@author: Jonathan Yu
'''
from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets
from shiboken2 import wrapInstance

import maya.cmds as cmds
import maya.OpenMaya as om
import maya.OpenMayaUI as omui


def maya_main_window():
    '''
    Return the Maya main window widget as a Python object
    '''
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)


class BatchMeshExport(QtWidgets.QDialog):
    
    def __init__(self, parent=maya_main_window()):
        super(BatchMeshExport, self).__init__(parent)
        
        self.setWindowTitle("Batch Export FBX Meshes")
        self.setMinimumWidth(400)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        
        self.create_widgets()
        self.create_layouts()
        self.create_connections()
        
    def create_widgets(self):
        self.exportFolderPath_le = QtWidgets.QLineEdit()
        self.select_exportFolderPath_btn = QtWidgets.QPushButton()
        self.select_exportFolderPath_btn.setIcon(QtGui.QIcon(":fileOpen.png"))
        self.select_exportFolderPath_btn.setToolTip("Select Folder")

        self.export_btn = QtWidgets.QPushButton("Export")
        self.close_btn = QtWidgets.QPushButton("Close")
        
    def create_layouts(self):
        exportFolderPath_layout = QtWidgets.QHBoxLayout()
        exportFolderPath_layout.addWidget(self.exportFolderPath_le)
        exportFolderPath_layout.addWidget(self.select_exportFolderPath_btn)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.export_btn)
        button_layout.addWidget(self.close_btn)

        form_layout = QtWidgets.QFormLayout()
        form_layout.addRow("Destination Folder:", exportFolderPath_layout)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(form_layout)
        main_layout.addLayout(button_layout)

    def create_connections(self):
    	self.select_exportFolderPath_btn.clicked.connect(self.show_folder_select_dialog)

        self.export_btn.clicked.connect(self.batch_export_FBX)
        self.close_btn.clicked.connect(self.close)

    def show_folder_select_dialog(self):
        folder_path = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Folder", "")
        if folder_path:
            self.exportFolderPath_le.setText(folder_path)

    def batch_export_FBX(self):
        folder_path = self.exportFolderPath_le.text()
        sel = cmds.ls(sl=True)
        numSel = len(sel)

        if (numSel < 1):
            om.MGlobal.displayError("Please select one or more objects!")
        else:
            folder_info = QtCore.QDir(folder_path)
            if not folder_info.exists():
                om.MGlobal.displayError("Folder does not exist: {0}".format(folder_path))
            else:
                for i in range(numSel):
                    filename = str(sel[i])
                    cmds.file("{0}/{1}.fbx".format(folder_path, filename), f=True, op="v=0;", es=True, typ="FBX export", pr=True)
                om.MGlobal.displayInfo("Successfully exported {0} object(s).".format(numSel))
        
        
if __name__ == "__main__":
    try:
        batchMeshExport.close()
        batchMeshExport.deleteLater()
    except:
        pass

    batchMeshExport = BatchMeshExport()
    batchMeshExport.show()