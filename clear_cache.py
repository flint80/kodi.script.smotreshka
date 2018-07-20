# -*- coding: utf-8 -*-

import os

import xbmc
import xbmcaddon

ADDON = xbmcaddon.Addon( id = 'script.smotreshka' )
ADDON_PATH = ADDON.getAddonInfo('path')
DATA_PATH = xbmc.translatePath( os.path.join( "special://profile/addon_data", 'script.smotreshka') )

def rmDir(dir_name):
    for file in os.listdir(dir_name):
        file_path = os.path.join(dir_name, file)
        if os.path.isfile(file_path):
            os.remove(file_path)
    os.rmdir(dir_name)


file_name = DATA_PATH + "/cookie"
if os.path.exists(file_name):
    os.remove(file_name)
file_name = DATA_PATH + "/thumbnails"
if os.path.exists(file_name):
    rmDir(file_name)
file_name = DATA_PATH + "/epg"
if os.path.exists(file_name):
    rmDir(file_name)
file_name = DATA_PATH + "/playback"
if os.path.exists(file_name):
    rmDir(file_name)
file_name = DATA_PATH + "/account"
if os.path.exists(file_name):
    os.remove(file_name)
file_name = DATA_PATH + "/channels"
if os.path.exists(file_name):
    os.remove(file_name)

xbmc.executebuiltin('XBMC.Notification("Смотрешка", "кеш очищен", %s, %s)' % (1234, ADDON.getAddonInfo('icon')))
