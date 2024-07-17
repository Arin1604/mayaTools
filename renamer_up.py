from maya import cmds

SUFFIXES = {
    "mesh":"geo",
    "joint":"jnt",
    "camera": None

}

DEFFAULT_SUFFIX = "grp"

def rename(selection=False):

    object = cmds.ls(selection=selection, dag=True, long=True)

    if selection and not object:
        raise RuntimeError("Nothing is selected")

    


    object.sort(key=len, reverse=True)
    for a in object:
    
        
        
        shortname = a.split("|")[-1]
        children = cmds.listRelatives(a, children=True) or []
        
        if len(children) == 1:
            child = children[0]
            objType = cmds.objectType(child)
            
        else:
            objType = cmds.objectType(a)
            
        
        suffix = SUFFIXES.get(objType, DEFFAULT_SUFFIX)

        if(a.endswith('_'+ suffix)):
            continue
            
        
        new_name = "%s_%s" % (shortname, suffix)
        cmds.rename(a, new_name)

        index = object.index(a)
        object[index] = a.replace(shortname, new_name)

    return object     
        
 


rename(True)
            
    

