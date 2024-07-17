from tweenerUI import tween
from gearClassCreator import Gear
from maya import cmds


class BaseWindow(object):

    windowName = "BaseWindow"

    def show(self):

        if cmds.window(self.windowName, query=True, exists=True):
            cmds.deleteUI(self.windowName)

        cmds.window(self.windowName)

        self.buildUI()
        cmds.showWindow()

    def buildUI(self):
        pass
    def reset(self, *args):
        pass
    def close(self, *args):
        cmds.deleteUI(self.windowName)

class TweenerWindow(BaseWindow):
    windowName = "TweenerWindow"

    def buildUI(self):
        column = cmds.columnLayout()

        cmds.text(label="Use the slider to set the tween amount")

        row = cmds.rowLayout(numberOfColumns=2)

        self.slider = cmds.floatSlider(min= 0, max=100, value=50, step= 1, changeCommand=tween)

        cmds.button(label="Reset", command=self.reset)

        cmds.setParent(column)
        cmds.button(label="Close", command= self.close)

    def reset(self, *args):
        print("Resetting tween")
        cmds.floatSlider(self.slider, edit=True, value = 50)

class GearUI(BaseWindow):
    windowName = "GearWindow"

    def __init__(self) -> None:
        self.gear = None

    def buildUI(self):
        column = cmds.columnLayout()
        cmds.text(label="This is the UI for gear generator")
        
        cmds.rowLayout(numberOfColumns=4)
        self.label = cmds.text(label='10')
        self.slider = cmds.intSlider(min=5, max=30, step=1, dragCommand=self.modifyGear)
        cmds.button(label="Make Gear", command=self.createGear)
        cmds.button(label="reset", command=self.reset)
        cmds.setParent(column)
        cmds.button(label="Close", command=self.close)


    def modifyGear(self, teeth):
        print(teeth)
        if self.gear:
            self.gear.changeTeeth(teeth=teeth)

        cmds.text(self.label, edit=True, label=teeth)
    
    def createGear(self, *args):
        print("Creating gear")
        teeth = cmds.intSlider(self.slider, query=True, value=True)

        self.gear = Gear()

        self.gear.createGear(teeth=teeth)
        

    def reset(self, *args):
        print("reset")
        self.gear = None
        cmds.intSlider(self.slider, edit=True, value=10)
        cmds.text(self.label, edit=True, label=10)

    