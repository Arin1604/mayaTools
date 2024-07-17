from maya import cmds

def createGear(teeth=10, length=0.3):
    print("Creating Gear {} , {}".format(teeth, length))

    #Teeth is every alternate span
    spans = teeth * 2

    transform, constructror = cmds.polyPipe(subdivisionsAxis=spans)
    sideFaces = range(spans *2, spans *3, 2 )

    cmds.select(clear=True)

    for face in sideFaces:
        print("This is pipe transform and constructor" + transform + constructror)
        cmds.select('{}.f[{}]'.format(transform, face), add=True)
    
    extrude = cmds.polyExtrudeFacet(localTranslateZ=length)[0]
    print(extrude)

    return transform, constructror, extrude

def changeTeeth(constructor, extrude, teeth=10, length=0.3):
    spans = teeth * 2

    cmds.polyPipe(constructor, edit=True, subdivisionsAxis=spans)

    sideFaces = range(spans *2, spans *3, 2 )
    faceNames = []

    for face in sideFaces:
        faceName =  'f[{}]'.format(face)
        faceNames.append(faceName)
    
    cmds.setAttr('{}.inputComponents'.format(extrude), len(faceNames), *faceNames, type="componentList")
    cmds.polyExtrudeFacet(extrude, edit=True, ltz=length)
