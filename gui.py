# Copyright (c) 2010-2011 Torrent-TV.RU
# Writer (c) 2011, Welicobratov K.A., E-mail: 07pov23@gmail.com

# imports
import xbmcaddon
import xbmc
import time
import xbmcgui
import threading
from mainform import WMainForm
#from player import MyPlayer
#from TSCore import TSengine as tsengine

#defines
ADDON = xbmcaddon.Addon( id = 'script.smotreshka' )
CANCEL_DIALOG  = ( 9, 10, 11, 92, 216, 247, 257, 275, 61467, 61448, )
ADDON_ICON	 = ADDON.getAddonInfo('icon')
ADDON_PATH = ADDON.getAddonInfo('path')
BTN_CHANNELS_ID = 102
BTN_TRANSLATIONS_ID = 103
BTN_CLOSE = 101



# functions
def showMessage(message = '', heading='Torrent-TV.RU', times = 3000, pics = ADDON_ICON):
	try: xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (heading.encode('utf-8'), message.encode('utf-8'), times, pics.encode('utf-8')))
	except Exception, e:
		try: xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (heading, message, times, pics))
		except Exception, e:
			xbmc.log( 'showMessage: exec failed [%s]' % 3 )


def main():
    ui = WMainForm("DialogDownloadProgress.xml", ADDON_PATH, 'default')
    ui.show()
    #thr = _DBThread(start, None)
    #thr.start()
    #xbmc.executebuiltin( "XBMC.PreviousMenu")
    while not ui.IsCanceled():
        #del ui
        #label = ui.getControl(104)
        #label.setVisible(False)
        
        xbmc.sleep(975)