import defines

#defines.showMessage("settings_manager init")

def getSetting(name, default = "", save = True):
    res = defines.ADDON.getSetting(name)
    if res == "":
        res = default
        if res != "" and save:
            defines.ADDON.setSetting(name, res)

    return res

def getSettingDef(name, name_cat):
    import xml.etree.ElementTree as ET
    import os
    path = os.path.join(defines.ADDON_PATH, "resource/setting.xml")
    tree = ET.parse(path)
    xcat = [c for c in tree.getroot().findall("category") if c.attrib["label"] == name_cat][0]
    return [s for s in xcat.findall("settings") if s.attrib["id"] == name][0].attrib
        
def setSettingDef(name, name_cat, attrib, value):
    import xml.etree.ElementTree as ET
    import os
    path = os.path.join(defines.ADDON_PATH, "resource/setting.xml")
    tree = ET.parse(path)
    xcat = [c for c in tree.getroot().findall("category") if c.attrib["label"] == name_cat][0]
    xel = [s for s in xcat.findall("settings") if s.attrib["id"] == name][0]
    xel.set(attrib, value)
    tree.write(path)

def setSetting(name, value):
    defines.ADDON.setSetting(name, value)