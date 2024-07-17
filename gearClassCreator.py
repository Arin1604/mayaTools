from maya import cmds

class Gear(object):

    def __init__(self) -> None:
        self.extrude = None
        self.constructor = None
        self.transform = None

    def createGear(self, teeth = 10, length = 0.3, pos = 0):
        
        spans = teeth * 2

        self.transform, self.constructor = cmds.polyPipe(subdivisionsAxis=spans)
        cmds.move(pos, y=True, x=True, z=True)
        sideFaces = range(spans *2, spans *3, 2 )

        cmds.select(self.transform)
        

        cmds.select(clear=True)

        for face in sideFaces:
            print("This is pipe transform and constructor" + self.transform + self.constructor)
            cmds.select('{}.f[{}]'.format(self.transform, face), add=True)
        
        self.extrude = cmds.polyExtrudeFacet(localTranslateZ=length)[0]
        
     

        
        #return transform, constructror, extrude
    
    def changeTeeth(self, teeth=10, length=0.3):
        spans = teeth * 2

        cmds.polyPipe(self.constructor, edit=True, subdivisionsAxis=spans)

        sideFaces = range(spans *2, spans *3, 2 )
        faceNames = []

        for face in sideFaces:
            faceName =  'f[{}]'.format(face)
            faceNames.append(faceName)
        
        cmds.setAttr('{}.inputComponents'.format(self.extrude), len(faceNames), *faceNames, type="componentList")
        cmds.polyExtrudeFacet(self.extrude, edit=True, ltz=length)
