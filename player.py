# Copyright (c) 2014 Torrent-TV.RU
# Writer (c) 2014, Welicobratov K.A., E-mail: 07pov23@gmail.com

import datetime
import threading
import time

import xbmc
import xbmcgui

import defines
import smotreshka

#defines
CANCEL_DIALOG  = ( 9, 10, 11, 92, 216, 247, 257, 275, 61467, 61448, )

def LogToXBMC(text, type = 1):
    ttext = ''
    if type == 2:
        ttext = 'ERROR:'
    print '[MyPlayer %s] %s %s\r' % (time.strftime('%X'),ttext, text)



class MyPlayer(xbmcgui.WindowXML):
    CONTROL_EPG_ID = 109
    CONTROL_PROGRESS_ID = 110
    CONTROL_ICON_ID = 202
    CONTROL_WINDOW_ID = 203
    CONTROL_BUTTON_PAUSE = 204
    CONTROL_BUTTON_INFOWIN = 209
    CONTROL_BUTTON_STOP = 200
    ACTION_RBC = 101

    def __init__(self, *args, **kwargs):
        self.played = False
        self.thr = None
        self.parent = None
        self.li = None
        self.visible = False
        self.t = None
        self.focusId = 203
        login = defines.getSetting("login","", False)
        password = defines.getSetting("password","", False)
        self.smApi = smotreshka.Smotreshka(login, password, defines.DATA_PATH)


    def onInit(self):
        if not self.li:
            return

        cicon = self.getControl(MyPlayer.CONTROL_ICON_ID)
        cicon.setImage(self.li.getProperty('icon'))
        if not self.parent:
            return
        self.UpdateEpg()
        self.getControl(MyPlayer.CONTROL_WINDOW_ID).setVisible(False)
        self.setFocusId(MyPlayer.CONTROL_EPG_ID)

    def UpdateEpg(self):
        if not self.li:
            return
        epg_id = self.li.getProperty("channel_uid")
        controlEpg = self.getControl(MyPlayer.CONTROL_EPG_ID)
        controlEpg1 = self.getControl(112)
        progress = self.getControl(MyPlayer.CONTROL_PROGRESS_ID)
        if epg_id and self.parent.epg.has_key(epg_id) and self.parent.epg[epg_id].__len__() > 0:
            ctime = datetime.datetime.now()
            curepg = self.parent.epg[epg_id][0]
            bt = curepg.startDate
            et = curepg.endDate
            percent = (ctime - bt).total_seconds()*100/((et-bt).total_seconds())
            self.progress.setPercent(percent)
            controlEpg.setLabel('%.2d:%.2d - %.2d:%.2d %s' % (bt.hour, bt.minute, et.hour, et.minute, curepg.title))
        else:
            controlEpg.setLabel('Нет программы')
            #controlEpg1.setLabel('')
            progress.setPercent(1)

    def Stop(self):
        print 'CLOSE STOP'
        #self.TSPlayer.thr.error = Exception('Stop player')
        xbmc.executebuiltin('PlayerControl(Stop)')

    def Start(self, li):
        self.StartProxy(li)
        return;

    def StartProxy(self, li):

        lit= xbmcgui.ListItem(li.getLabel())
        url = self.smApi.get_play_url(li.getProperty("channel_uid"))

        xbmc.Player().play(url, lit)


    def hide(self):
        pass
        #xbmc.executebuiltin('Action(ParentDir)')
        #if self.TSPlayer.playing:
        #    xbmc.executebuiltin('Action(ParentDir)')
        #    print 'Главное меню'

    def getPlayed(self):
        return self.played

    def hideControl(self):
        self.getControl(MyPlayer.CONTROL_WINDOW_ID).setVisible(False)
        self.setFocusId(MyPlayer.CONTROL_WINDOW_ID)
        self.focusId = MyPlayer.CONTROL_WINDOW_ID



    def onAction(self, action):
        if action in CANCEL_DIALOG:
            LogToXBMC('Closes player %s %s' % (action.getId(), action.getButtonCode()))
            self.close()
        elif action.getId() == MyPlayer.ACTION_RBC:
            LogToXBMC('CLOSE PLAYER 101 %s %s' % (action.getId(), action.getButtonCode()))
            self.close()
        elif action.getId() == 0 and action.getButtonCode() == 61530:
            xbmc.executebuiltin('Action(FullScreen)')
            xbmc.sleep(4000)
            xbmc.executebuiltin('Action(Back)')

        wnd = self.getControl(MyPlayer.CONTROL_WINDOW_ID)
        if not self.visible:
            self.UpdateEpg()
            wnd.setVisible(True)
            if self.focusId == MyPlayer.CONTROL_WINDOW_ID:
                self.setFocusId(MyPlayer.CONTROL_BUTTON_PAUSE)
            else:
                self.setFocusId(self.focusId)
            self.setFocusId(self.getFocusId())
            if self.t:
                self.t.cancel()
                self.t = None
            self.t = threading.Timer(4, self.hideControl)
            self.t.start()

    def onClick(self, controlID):
        if controlID == MyPlayer.CONTROL_BUTTON_STOP:
            self.close()
        if controlID == self.CONTROL_BUTTON_INFOWIN:
            self.parent.showInfoWindow()
