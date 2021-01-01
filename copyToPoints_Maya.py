'''
NAME
Copy To Points Tool

DESCRIPTION
Copies object set by user to selected vertex (or vertices), with option to use target vertex orientation

v1.0
Created on January 1, 2021
@author: Jonathan Yu
'''
from PySide2 import QtCore
from PySide2 import QtWidgets
from shiboken2 import wrapInstance

import maya.cmds as cmds
import maya.OpenMaya as om
import maya.OpenMayaUI as omui


# Return normal vector of selected face
def normalVector(selFace):
    polyNormal = cmds.polyInfo(selFace, fn=True)[0].split(':')[1].split()

    normalX = float(polyNormal[0])
    normalY = float(polyNormal[1])
    normalZ = float(polyNormal[2])
    normalVector = [normalX, normalY, normalZ]
    return normalVector

def maya_main_window():
    '''
    Return the Maya main window widget as a Python object
    '''
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)


class CopyToPoints(QtWidgets.QDialog):
    
    def __init__(self, parent=maya_main_window()):
        super(CopyToPoints, self).__init__(parent)
        
        self.setWindowTitle("Copy To Points")
        self.setMinimumWidth(200)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        
        self.create_widgets()
        self.create_layouts()
        self.create_connections()
        
    def create_widgets(self):
        self.groupName_le = QtWidgets.QLineEdit()
        self.setTargetObject_btn = QtWidgets.QPushButton("Set Object to Copy")
        self.targetOrientation_cb = QtWidgets.QCheckBox("Use Target Vertex Orientation")
        self.targetOrientation_cb.setChecked(1)

        self.apply_btn = QtWidgets.QPushButton("Apply")
        self.close_btn = QtWidgets.QPushButton("Close")
        
    def create_layouts(self):
        group_name_layout = QtWidgets.QHBoxLayout()
        group_name_layout.addWidget(self.groupName_le)

        trgt_obj_settings_layout = QtWidgets.QVBoxLayout()
        trgt_obj_settings_layout.addWidget(self.setTargetObject_btn)
        trgt_obj_settings_layout.addWidget(self.targetOrientation_cb)

        form_layout = QtWidgets.QFormLayout()
        form_layout.addRow("Group Name:", group_name_layout)
        form_layout.addRow(trgt_obj_settings_layout)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.apply_btn)
        button_layout.addWidget(self.close_btn)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(form_layout)
        main_layout.addLayout(button_layout)

    def create_connections(self):
        self.setTargetObject_btn.clicked.connect(self.set_target_object)

        self.apply_btn.clicked.connect(self.copy_to_pts)
        self.close_btn.clicked.connect(self.close)

    def set_target_object(self):
        sel = cmds.ls(sl=True)
        numSel = len(sel)
        if numSel < 1:
            om.MGlobal.displayError("Please select an object!")
        elif numSel > 1:
            om.MGlobal.displayError("Please only select one single object!")
        else:
            self.targetObject = cmds.ls(sl=True)[0]
            om.MGlobal.displayInfo("{0} has been set as the object to copy".format(self.targetObject))

    '''
    Copy to Points Tool
    '''
    def copy_to_pts(self):
        sel = cmds.ls(sl=True, flatten=True)
        numVerts = len(sel)
        if (numVerts < 1) or ".vtx" not in sel[0]:
            om.MGlobal.displayError("Please select one or more vertices")
        else:
            selName = sel[0].split('.vtx')[0]
            if self.groupName_le.text():
                grpName = cmds.group(em=True, n="{0}_grp".format(self.groupName_le.text()))
            else:
                grpName = cmds.group(em=True, n="group1")
            targetObj = self.targetObject

            # Freeze all transformations
            cmds.makeIdentity(selName, apply=True)

            for vertNum in range(numVerts):
                # Get position XYZ values of current vertex
                pointPos = cmds.pointPosition(sel[vertNum])
                # Duplicate target object, add to group, and move to position of current vertex
                dupeObj = cmds.duplicate(targetObj)
                cmds.parent(dupeObj, grpName)
                cmds.move(pointPos[0], pointPos[1], pointPos[2])
                
                if self.targetOrientation_cb.isChecked():
                    # Return a list of face numbers connecteed to selected vertex
                    vertFaces = str(cmds.polyInfo(sel[vertNum], vf=True)[0].split(':')[1]).split()
                    numFaces = len(vertFaces)
                    # Get average normal vector of current vertex
                    avgNormal = [0.0, 0.0, 0.0]
                    for i in range(numFaces):
                        vertFaces[i] = int(vertFaces[i])
                        curNormal = normalVector('{0}.f[{1}]'.format(selName, vertFaces[i]))
                        avgNormal[0] += curNormal[0]
                        avgNormal[1] += curNormal[1]
                        avgNormal[2] += curNormal[2]
                    # Get a Euler rotation value to orient target object to the average normal vector and rotate accordingly
                    rot = cmds.angleBetween(euler=True, v1=(0.0, 1.0, 0.0), v2=avgNormal)
                    cmds.rotate(str(rot[0])+'deg', str(rot[1])+'deg', str(rot[2])+'deg', r=True, ws=True, fo=True)
                
                '''
                WIP Local rotation to point target object towards next point
                '''
                # Get a local Euler rotation value to point target object at next vertex and rotate target object accordingly
                # if numVerts > 1:
                #     if vertNum == numVerts-1:
                #         pointPos1 = cmds.pointPosition(sel[vertNum])
                #         pointPos2 = cmds.pointPosition(sel[vertNum-1])
                #         dirVector = [-(pointPos2[0]-pointPos1[0]),
                #                     -(pointPos2[1]-pointPos1[1]),
                #                     -(pointPos2[2]-pointPos1[2])
                #                     ]
                #         localRot = cmds.angleBetween(euler=True, v1=(0.0, 0.0, 1.0), v2=dirVector)
                #     else:
                #         pointPos1 = cmds.pointPosition(sel[vertNum])
                #         pointPos2 = cmds.pointPosition(sel[vertNum+1])
                #         dirVector = [pointPos2[0]-pointPos1[0],
                #                     pointPos2[1]-pointPos1[1],
                #                     pointPos2[2]-pointPos1[2]
                #                     ]
                #         localRot = cmds.angleBetween(euler=True, v1=(0.0, 0.0, 1.0), v2=dirVector)
                #     cmds.rotate(str(localRot[0])+'deg', str(localRot[1])+'deg', str(localRot[2])+'deg', r=True, ws=True, fo=True)
                    
            # Set selection to original selection
            cmds.select(grpName)
        
        
if __name__ == "__main__":
    try:
        copyToPoints.close()
        copyToPoints.deleteLater()
    except:
        pass

    copyToPoints = CopyToPoints()
    copyToPoints.show()