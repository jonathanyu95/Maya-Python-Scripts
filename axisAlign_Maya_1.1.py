'''
NAME
Axis Align Tool

DESCRIPTION
Aligns selected objects along all 3 axes based upon selected change types.

v1.1
Updated on December 2, 2020
Created on December 1, 2020
@author: Jonathan Yu
'''
from PySide2 import QtCore
from PySide2 import QtWidgets
from shiboken2 import wrapInstance

import maya.cmds as mc
import maya.OpenMaya as om
import maya.OpenMayaUI as omui


def avg(minP, maxP):
    return (minP + maxP)/2
    
def moveDist(changeType, bBox_min, bBox_max, centroid):
    if changeType == 1:
        return -centroid
    elif changeType == 2:
        return -bBox_min
    elif changeType == 3:
        return -bBox_max
    return 0

def maya_main_window():
    '''
    Return the Maya main window widget as a Python object
    '''
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)


class AxisAlign(QtWidgets.QDialog):
    
    def __init__(self, parent=maya_main_window()):
        super(AxisAlign, self).__init__(parent)
        
        self.setWindowTitle("Axis Align")
        self.setMinimumWidth(200)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        
        self.create_widgets()
        self.create_layouts()
        self.create_connections()
        
    def create_widgets(self):
        self.axisX = QtWidgets.QComboBox()
        self.axisX.addItems(["No Change", "Center", "Min", "Max"])
        self.axisX.setCurrentIndex(1)
        self.axisY = QtWidgets.QComboBox()
        self.axisY.addItems(["No Change", "Center", "Min", "Max"])
        self.axisY.setCurrentIndex(2)
        self.axisZ = QtWidgets.QComboBox()
        self.axisZ.addItems(["No Change", "Center", "Min", "Max"])
        self.axisZ.setCurrentIndex(1)

        self.unitSize_cb = QtWidgets.QCheckBox("Make Unit Size")

        self.apply_btn = QtWidgets.QPushButton("Apply")
        self.close_btn = QtWidgets.QPushButton("Close")
        
    def create_layouts(self):
        form_layout = QtWidgets.QFormLayout()
        form_layout.addRow("X Axis:", self.axisX)
        form_layout.addRow("Y Axis:", self.axisY)
        form_layout.addRow("Z Axis:", self.axisZ)
        form_layout.addRow("", self.unitSize_cb)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.apply_btn)
        button_layout.addWidget(self.close_btn)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(form_layout)
        main_layout.addLayout(button_layout)

    def create_connections(self):
        self.apply_btn.clicked.connect(self.align_objects)
        self.close_btn.clicked.connect(self.close)

    def align_objects(self):
        selObj = mc.ls(sl=True)
        numSel = len(selObj)
        if (numSel < 1):
            om.MGlobal.displayError("Please select one or more objects!")
        else:
            bBox = mc.exactWorldBoundingBox()
            if self.unitSize_cb.isChecked():
                sizeX = (bBox[3] - bBox[0])
                sizeY = (bBox[4] - bBox[1])
                sizeZ = (bBox[5] - bBox[2])
                scale = 1 / max(sizeX, sizeY, sizeZ)

                mc.scale(scale, scale, scale, selObj, cp=True, r=True)

            bBox = mc.exactWorldBoundingBox()
            bBox_min = bBox[:3]
            bBox_max = bBox[3:]
            centroid = [
                avg(bBox_min[0], bBox_max[0]),
                avg(bBox_min[1], bBox_max[1]),
                avg(bBox_min[2], bBox_max[2])
                ]
            
            axisX = self.axisX.currentIndex()
            axisY = self.axisY.currentIndex()
            axisZ = self.axisZ.currentIndex()
            
            mc.move(
                moveDist(axisX, bBox_min[0], bBox_max[0], centroid[0]),
                moveDist(axisY, bBox_min[1], bBox_max[1], centroid[1]),
                moveDist(axisZ, bBox_min[2], bBox_max[2], centroid[2]),
                selObj, r=True)
        
        
if __name__ == "__main__":
    try:
        axis_align.close()
        axis_align.deleteLater()
    except:
        pass

    axis_align = AxisAlign()
    axis_align.show()