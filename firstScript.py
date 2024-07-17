from maya import cmds

cube = cmds.polyCube()
print(cube)

cubeShape = cube[0]

circle = cmds.circle()
type(circle)
circleShape = circle[0]

print(circle[0])
print(type(circle))

cmds.parent(cubeShape, circleShape)
cmds.setAttr(cubeShape + ".translate", lock = True)
cmds.setAttr(cubeShape + ".scale", lock = True)
cmds.setAttr(cubeShape + ".rotate", lock = True)
cmds.select(circleShape)
