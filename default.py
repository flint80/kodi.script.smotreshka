# Copyright (c) 2013 Torrent-TV.RU
# Writer (c) 2011, Welicobratov K.A., E-mail: 07pov23@gmail.com

import defines
import smotreshka

import mainform

if __name__ == '__main__':
    if not defines.ADDON.getSetting("login"):
        defines.ADDON.setSetting("login", "tv035");
        defines.ADDON.setSetting("password", "Snrhfyb7dnkc")

    w = mainform.WMainForm("mainform.xml", defines.SKIN_PATH, "st.anger")
    w.doModal()
    del w
