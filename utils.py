# -*- coding: utf-8 -*-

import xbmcaddon
import xbmc
import sys
import threading
import os


ADDON = xbmcaddon.Addon( id = 'script.smotreshka' )
ADDON_PATH = ADDON.getAddonInfo('path')
ADDON_ICON = ADDON.getAddonInfo('icon')
DATA_PATH = xbmc.translatePath( os.path.join( "special://profile/addon_data", 'script.smotreshka') )


class MyThread(threading.Thread):
    def __init__(self, func, params):
        threading.Thread.__init__(self)
        self.func = func
        self.params = params

    def run(self):
        self.func(self.params)
    def stop(self):
        pass

if (sys.platform == 'win32') or (sys.platform == 'win64'):
    ADDON_PATH = ADDON_PATH.decode('utf-8')

def showMessage(message = '', heading='Смотрешка', times = 1234):
    try: 
        xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, %s)' % (heading.encode('utf-8'), message.encode('utf-8'), times, ADDON_ICON))
    except Exception, e:
        try: xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, %s)' % (heading, message, times, ADDON_ICON))
        except Exception, e:
            xbmc.log( 'showMessage: exec failed [%s]' % 3 )

def getSetting(name):
    return ADDON.getSetting(name)


