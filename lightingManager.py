import time
from Qt import QtWidgets, QtCore, QtGui
from maya import cmds
from functools import partial
import Qt
import logging
from maya import OpenMayaUI as omui
import json
import os


logging.basicConfig()
logger = logging.getLogger('LightingManager')
logger.setLevel(logging.DEBUG)

if Qt.__binding__ == 'PySide':
     logger.debug('USING PySIde with shiboken')
     from shiboken import wrapInstance
     from QtCore import Signal

elif Qt.__binding__.startswith('PyQt'):
     logger.debug('USING PyQT with shiboken')

     from sip import wrapinstance as wrapInstance
     from QtCore import pyqtSignal as Signal

     
else:
     logger.debug('USING PySIde2 with shiboken')

     #from shiboken6 import Shiboken
     from shiboken6 import wrapInstance as wrapInstance
     from Qt.QtCore import Signal


def getMayaMainWindow():
     win = omui.MQtUtil.mainWindow()
     ptr = wrapInstance(int(win), QtWidgets.QMainWindow)
     return ptr

def getDock(name='LightingManagerDock'):
     deleteDock(name)
     ctrl = cmds.workspaceControl(name, dockToMainWindow=('right', 1), label="Lighting Manager")
     qtCtrl = omui.MQtUtil.findControl(ctrl)
     ptr = wrapInstance(int(qtCtrl), QtWidgets.QWidget)
     return ptr


def deleteDock(name='LightingManagerDock'):
     if cmds.workspaceControl(name, query=True, exists=True):
          cmds.deleteUI(name)
     
class LightManager(QtWidgets.QWidget):

    lightTypes = {
        "Point Light": cmds.pointLight,
        "Spot Light": cmds.spotLight,
        "Directional Light": cmds.directionalLight,
        "Area Light": partial(cmds.shadingNode, 'areaLight', asLight=True),
        "Volume Light": partial(cmds.shadingNode, 'volumeLight', asLight=True)
    }

    def __init__(self, dock=True):
        
     #   parent = getMayaMainWindow()
     if dock:
        parent = getDock()
     else:
        deleteDock()
        try:
            cmds.deleteUI('lightingManager')
        except:
             logger.debug('No prev UI exists')

        parent = QtWidgets.QDialog(parent=getMayaMainWindow())
        parent.setObjectName('lightingManager')
        parent.setWindowTitle('Lighting Manager')
        dlgLayout = QtWidgets.QVBoxLayout(parent)


     self.Window_Title = "Light Manager"
     super(LightManager, self).__init__(parent=parent)
     self.buildUI()
     self.populate()

     self.parent().layout().addWidget(self)
     if not dock:
             parent.show()

    def populate(self):
        while self.scrollLayout.count():
            widget = self.scrollLayout.takeAt(0).widget()
            if widget:
                 widget.setVisible(False)
                 widget.deleteLater()

        for light in cmds.ls(type=["areaLight", "spotLight", "pointLight", "directionalLight", "volumeLight"]):
             self.addLight(light)
            # PyMel gives us back a PyNode for each object it lists

        

    def buildUI(self):
        layout = QtWidgets.QGridLayout(self)



        self.lightTypeCB = QtWidgets.QComboBox()
        layout.addWidget(self.lightTypeCB, 0, 0, 1, 2)

        for lightType in sorted(self.lightTypes):
            self.lightTypeCB.addItem(lightType)

        createBTN = QtWidgets.QPushButton('create')
        createBTN.clicked.connect(self.createLight)
        layout.addWidget(createBTN, 0, 2)

        scroll_widget = QtWidgets.QWidget()
        scroll_widget.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        self.scrollLayout = QtWidgets.QVBoxLayout(scroll_widget)

        scroll_area= QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(scroll_widget)

        layout.addWidget(scroll_area, 1, 0, 1, 3)

        saveBtn = QtWidgets.QPushButton('Save')
        saveBtn.clicked.connect(self.saveLights)
        layout.addWidget(saveBtn, 2, 0)

        importBtn = QtWidgets.QPushButton('Import')
        importBtn.clicked.connect(self.importLights)
        layout.addWidget(importBtn, 2, 1)


        refreshBtn = QtWidgets.QPushButton('Refresh')
        refreshBtn.clicked.connect(self.populate)
        layout.addWidget(refreshBtn, 2, 2)

    def saveLights(self):
         properties = {}

         for lightWidget in self.findChildren(LightWidget):
              light = lightWidget.light
              transform = cmds.listRelatives(light, parent=True, type='transform')
              if transform:
                        transform = transform[0]
              else:
                        transform = light 
            
              translate = cmds.getAttr(f"{transform}.translate")[0]
              rotation = cmds.getAttr(f"{transform}.rotate")[0]
              lightType = cmds.objectType(light)
              intensity = cmds.getAttr(f"{light}.intensity")
              color = cmds.getAttr(f"{light}.color")[0]

              properties[str(transform)] = {
                   'translate': list(translate),
                   'rotation': list(rotation),
                   'lightType': lightType,
                   'intensity': intensity,
                   'color': list(color)

              }  

         directory = self.getDirectory()

         lightFile = os.path.join(directory, 'lightFile_%s.json' % time.strftime('%m%d'))

         with open(lightFile, 'w') as f:
              json.dump(properties, f, indent=4)

         logger.info('Saving file to %s' % lightFile)


    
    def getDirectory(self):
    # The getDirectory method will give us back the name of our library directory and create it if it doesn't exist
        user_app_dir = cmds.internalVar(userAppDir=True)
        directory = os.path.join(user_app_dir, 'lightManager')
        if not os.path.exists(directory):
            os.mkdir(directory)
        return directory
         



    def importLights(self):
        directory = self.getDirectory()
        fileName = QtWidgets.QFileDialog.getOpenFileName(self, "Light Browser", directory)
        with open(fileName[0], 'r') as f:
             properties= json.load(f)
        
        for light, info in properties.items():
             lightType = info.get('lightType')
             for lt in self.lightTypes:
                   
                  if (f'{lt.split()[0].lower()}Light') == lightType:
                       break
             else:
                  logger.info(f'Cant find the appropriate light type for {light}{lightType}')
                  continue
                  
             light = self.createLight(curr_light=lt)
             intensity = info.get('intensity')
             if intensity is not None:
                cmds.setAttr(f"{light}.intensity", intensity)

             transform = cmds.listRelatives(light, parent=True)[0]


             translate = info.get('translate')
             if translate:
                cmds.setAttr(f"{transform}.translate", translate[0], translate[1], translate[2])

             rotation = info.get('rotation')
             if rotation:
                cmds.setAttr(f"{transform}.rotate", rotation[0], rotation[1], rotation[2])

             self.populate()


    def createLight(self, curr_light = None, add=True):

        if not curr_light:
            curr_light = self.lightTypeCB.currentText()
        
        light = self.lightTypes[curr_light]()
        print('This is the light that was created {}'.format(light))
        transform = cmds.listRelatives(light, parent=True, type='transform')

        print(f'This is the transform: {transform}')
        
        if add:
            self.addLight(light)

        return light
        
        
        # light_obj = cmds.ls(light)
        # relatives = cmds.listRelatives(light, shapes=True)
      

        # transform = cmds.listRelatives(light, parent=True)[0]
        # print(transform)
        # # transform = relatives[0]

        # # attrs = cmds.getAttr(transform)


        # # print(attrs)
    
    def addLight(self, light):
        widget = LightWidget(light=light)
        self.scrollLayout.addWidget(widget)
        widget.onSolo.connect(self.onSoloFunc)
        return light
    
    def onSoloFunc(self, val):
         lightWidgets = self.findChildren(LightWidget)
         print(lightWidgets)
         for widget in lightWidgets:
              if widget != self.sender():
                   widget.disableLight(val)

class LightWidget(QtWidgets.QWidget):

    onSolo = Signal(bool)

    def __init__(self, light):
          super(LightWidget, self).__init__()

          if isinstance(light, str):
             logger.debug('Converting node to a DagPath')
             if cmds.objExists(light):
                light = cmds.ls(light, dag=True, shapes=True)[0]

        # We might also get passed the transform instead of the light shape, either as a name or a DagPath.
        # So we'll check if it's a transform node and then get the shape
          if cmds.objectType(light) == 'transform':
                shapes = cmds.listRelatives(light, shapes=True)
                if shapes:
                    light = shapes[0]


          self.light = light
          self.buildUI()
    
    def buildUI(self):
        layout = QtWidgets.QGridLayout(self)
        
        # transform = cmds.listRelatives(self.light, parent=True)
        # if transform:
        #  transform = transform[0]
        # else:
        #  transform = self.light

        transform = cmds.listRelatives(self.light, parent=True, type='transform')
        if transform:
            transform = transform[0]
        else:
            transform = self.light

        # We make a checkbox with the label of our Light node's transform
        self.name = name = QtWidgets.QCheckBox(str(transform))
        
        # Let's make sure its value is the same as the transform node's visibility
        visibility_attr = f"{transform}.visibility"
        visibility = cmds.getAttr(visibility_attr)
        name.setChecked(visibility)

        # We connect the toggled signal from the checkbox to a lambda
        name.toggled.connect(lambda val: cmds.setAttr(visibility_attr, val))

        # Finally we add it to the layout in position 0, 0 (row 0, column 0)
        layout.addWidget(name, 0, 0)

        soloBtn = QtWidgets.QPushButton('Solo')
        soloBtn.setCheckable(True)
        soloBtn.toggled.connect(lambda val: self.onSolo.emit(val))
        layout.addWidget(soloBtn, 0, 1)

        deleteBtn = QtWidgets.QPushButton('X')
        deleteBtn.clicked.connect(self.deleteLight)
        deleteBtn.setMaximumWidth(50)
        layout.addWidget(deleteBtn, 0, 2)

        intensity = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        intensity.setMinimum(1)
        intensity.setMaximum(1000)
        intensity_attr = f"{transform}.intensity"
        intensity_val = cmds.getAttr(intensity_attr)
        intensity.setValue(intensity_val)
        intensity.valueChanged.connect(lambda val: cmds.setAttr(intensity_attr, val))
        layout.addWidget(intensity,1,0,1,2 )

        self.colorBtn = QtWidgets.QPushButton()
        self.colorBtn.setMaximumWidth(20)
        self.colorBtn.setMaximumHeight(20)
        self.setButtonColor()
        self.colorBtn.clicked.connect(self.setColor)
        layout.addWidget(self.colorBtn, 1,2)

    def setButtonColor(self, color=None):
        if not color:
              color_attr = f'{self.light}.color'
              color_val = cmds.getAttr(color_attr)
              print(f'This is color {color_val} and its length is {len(color_val)}')
              color = color_val[0]

        assert len(color) == 3, "MUST GIVE COLOR WITH 3 VALUES"

        r,g,b = [c * 255 for c in color]

        self.colorBtn.setStyleSheet('background-color: rgba(%s, %s, %s, 1.0);' % (r, g, b))         

    def setColor(self):
        color_attr = f'{self.light}.color'
        color_val = cmds.getAttr(color_attr)[0]
        cmds.colorEditor(rgb=color_val)

        if cmds.colorEditor(query=True, result=True):
        # Get the new color values from the color editor
            new_color = cmds.colorEditor(query=True, rgb=True)
        
        # Update the light's color attribute with the new values
            cmds.setAttr(color_attr, new_color[0], new_color[1], new_color[2])
        
        # Update the color button with the new color
            self.setButtonColor(new_color)
        else:
        # If the color editor was canceled, just keep the old color
            print("Color editor was canceled")





    def disableLight(self, val):
         self.name.setChecked(not val)

    def deleteLight(self):
         self.setParent(None)
         self.setVisible(False)
         self.deleteLater()

         transform = cmds.listRelatives(self.light, parent=True, type='transform')
         if transform:
                transform = transform[0]
         else:
                transform = self.light

         cmds.delete(transform)

    
    
    
# def showUI():
#         ui = LightManager()
        
#         ui.show()
#         return ui