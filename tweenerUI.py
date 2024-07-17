from maya import cmds





def tween(percentage, obj=None, attrs=None, selection=True):
    #Case where there is no selection and no object is given
    if not obj and not selection:
        raise ValueError("No Object Given To Tween")
    
    #if no obj is given, but selection is true, set obj to the first object that is selected

    if not obj:
        obj = cmds.ls(selection=True)[0]

    if not attrs:
        attrs = cmds.listAttr(obj, keyable=True)
    
    print(obj,attrs)
    currentTime = cmds.currentTime(query=True)
    print(currentTime)

    for attr in attrs:
        #Names the full name of the attribute
        attr_full = '{}.{}'.format(obj, attr)
        
        #Get the keyframes on this attribute
        keyframes = cmds.keyframe(attr_full, query=True)

        if not keyframes:
            continue

        previousKeyframes = []
        for k in keyframes:
            if k < currentTime:
                previousKeyframes.append(k)

        laterKeyFrames = [frame for frame in keyframes if frame > currentTime]

        if not previousKeyframes and not laterKeyFrames:
            continue

        if previousKeyframes:
            previousFrame = max(previousKeyframes)
        else:
            previousFrame = None
        
        nextFrame = min(laterKeyFrames) if laterKeyFrames else None

        

        if not previousFrame or not nextFrame:
            continue

        previousVal = cmds.getAttr(attr_full, time=previousFrame)
        nextVal = cmds.getAttr(attr_full, time=nextFrame)

        print("This is the attribute:{}'s previous value:{} and next value:{}".format(attr_full,previousVal, nextVal))

        difference = (nextVal - previousVal) * (percentage/100.0)
        currentVal = previousVal + difference

        cmds.setKeyframe(attr_full, time=currentTime, value=currentVal)


    print(keyframes)
#tween(20, selection=False)

class TweenWindow(object):

    windowName = "TweenerWindow"

    def show(self):

        if cmds.window(self.windowName, query=True, exists=True):
            cmds.deleteUI(self.windowName)

        cmds.window(self.windowName)

        self.buildUI()
        cmds.showWindow()

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

    def close(self, *args):
        cmds.deleteUI(self.windowName)