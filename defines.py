import xbmcaddon
import xbmc
import sys
import threading
import os


ADDON = xbmcaddon.Addon( id = 'script.smotreshka' )
ADDON_ICON	 = ADDON.getAddonInfo('icon')
ADDON_PATH = ADDON.getAddonInfo('path')
ADDON_ICON	 = ADDON.getAddonInfo('icon')
DATA_PATH = xbmc.translatePath( os.path.join( "special://profile/addon_data", 'script.smotreshka') )
ENGINE_NOXBIT = 0
ENGINE_AS = 1
ENGINE_PROXY = 2
VERSION = '1.5.3'
skin = ADDON.getSetting('skin')
SKIN_PATH = ADDON_PATH
smApi = None
print skin
if (skin != None) and (skin != "") and (skin != 'st.anger'):
    SKIN_PATH = DATA_PATH


class MyThread(threading.Thread):
    def __init__(self, func, params, back = True):
        threading.Thread.__init__(self)
        self.func = func
        self.params = params
        #self.parent = parent

    def run(self):
        self.func(self.params)
    def stop(self):
        pass

if (sys.platform == 'win32') or (sys.platform == 'win64'):
    ADDON_PATH = ADDON_PATH.decode('utf-8')

def showMessage(message = '', heading='Torrent-TV.RU', times = 1234):
    try: 
        xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, %s)' % (heading.encode('utf-8'), message.encode('utf-8'), times, ADDON_ICON))
    except Exception, e:
        try: xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, %s)' % (heading, message, times, ADDON_ICON))
        except Exception, e:
            xbmc.log( 'showMessage: exec failed [%s]' % 3 )

    

def tryStringToInt(str_val):
    try:
        return int(str_val)
    except:
        return 0


def getSetting(name, default="", save=True):
    res = ADDON.getSetting(name)
    if res == "":
        res = default
        if res != "" and save:
            ADDON.setSetting(name, res)

    return res


def getSettingDef(name, name_cat):
    import xml.etree.ElementTree as ET
    import os
    path = os.path.join(ADDON_PATH, "resources/settings.xml")
    tree = ET.parse(path)
    xcat = [c for c in tree.getroot().findall("category") if c.attrib["label"] == name_cat][0]
    return [s for s in xcat.findall("setting") if s.attrib["id"] == name][0].attrib


def setSettingDef(name, name_cat, attrib, value):
    import xml.etree.ElementTree as ET
    import os
    path = os.path.join(ADDON_PATH, "resources/settings.xml")
    tree = ET.parse(path)
    xcat = [c for c in tree.getroot().findall("category") if c.attrib["label"] == name_cat][0]

    xel = [s for s in xcat.findall("setting") if s.attrib["id"] == name][0]
    xel.set(attrib, value)
    tree.write(path)


def setSetting(name, value):
    ADDON.setSetting(name, value)