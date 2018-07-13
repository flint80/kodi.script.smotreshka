# Copyright (c) 2013 Torrent-TV.RU
# Writer (c) 2013, Welicobratov K.A., E-mail: 07pov23@gmail.com

import datetime
import json
import time

import xbmc
# imports
import xbmcgui

# import settings_manager
import defines
import smotreshka
from adswnd import AdsForm
from player import MyPlayer


#defines.showMessage("mainform init")

def LogToXBMC(text, type = 1):
    ttext = ''
    if type == 2:
        ttext = 'ERROR:'
    print '[MainForm %s] %s %s\r' % (time.strftime('%X'),ttext, text)

class WMainForm(xbmcgui.WindowXML):
    CANCEL_DIALOG  = ( 9, 10, 11, 92, 216, 247, 257, 275, 61467, 61448, )
    CONTEXT_MENU_IDS = (117, 101)
    ARROW_ACTIONS = (1,2,3,4)
    ACTION_MOUSE = 107
    BTN_VOD_ID = 113
    BTN_CLOSE = 101
    BTN_FULLSCREEN = 208
    IMG_SCREEN = 210
    CONTROL_LIST = 50
    PANEL_ADS = 105
    PROGRESS_BAR = 110
    BTN_INFO = 209
    LBL_FIRST_EPG = 300
    BTN_NEWS_CATEGORY_ID = 106
    BTN_MOVIES_CATEGORY_ID = 105
    BTN_SPORT_CATEGORY_ID = 104
    BTN_AIR_CATEGORY_ID = 107
    BTN_FAVORITES_CATEGORY_ID = 102
    BTN_ALL_CHANNELS_CATEGORY_ID = 103


    def __init__(self, *args, **kwargs):
        self.isCanceled = False
        self.category = {}
        self.seltab = 0
        self.epg = {}
        self.archive = []
        self.selitem = '0'
        self.img_progress = None
        self.txt_progress = None
        self.list = None
        self.player = MyPlayer("player.xml", defines.SKIN_PATH, defines.ADDON.getSetting('skin'))
        self.player.parent = self
        self.amalkerWnd = AdsForm("adsdialog.xml", defines.SKIN_PATH, defines.ADDON.getSetting('skin'))
        self.cur_category = smotreshka.Smotreshka.FAVORITES_CATEGORY_ID
        self.epg = {}
        self.selitem_id = -1
        self.playditem = -1
        self.user = None
        login = defines.getSetting("login","", False)
        password = defines.getSetting("password","", False)
        self.smApi = smotreshka.Smotreshka(login, password, defines.DATA_PATH)
        self.infoform=None
        self.category = None
        self.cur_category=smotreshka.Smotreshka.FAVORITES_CATEGORY_ID

    def initLists(self):
        self.category={}

    def getChannels(self,param):
        channelsMap = self.smApi.get_channels()
        for cat in channelsMap:
            if not self.category.has_key(cat):
                self.category[cat] = []
                for ch in channelsMap[cat]:
                    li = xbmcgui.ListItem(ch.title, ch.uid, '', '')
                    li.setProperty("type", "channel")
                    li.setProperty("channel_uid", ch.uid)
                    li.setProperty("icon", ch.thumbnail)
                    self.category[cat].append(li)


    def getEpg(self, param):
        print "epg_param = " + param["uid"]
        epg = self.smApi.get_epg(param["uid"])

        self.epg[param["uid"]] = epg
        self.showSimpleEpg(param["uid"],param["icon"])
        self.hideStatus()

    def onInit(self):
        try:
            self.img_progress = self.getControl(1108)
            self.txt_progress = self.getControl(1107)
            self.progress = self.getControl(WMainForm.PROGRESS_BAR)
            self.updateList()

        except Exception, e:
            LogToXBMC('OnInit: %s' % e, 2)

    def onFocus(self, ControlID):
        if ControlID == 50:
            if not self.list:
                return
            selItem = self.list.getSelectedItem()
            if selItem:
                if selItem.getLabel2() == self.selitem or selItem.getLabel() == '..':
                    return
                self.selitem = selItem.getLabel2()
                self.selitem_id = self.list.getSelectedPosition()
                LogToXBMC('Selected %s' % self.selitem_id)
                channelUid = selItem.getProperty("channel_uid")
                icon = selItem.getProperty("icon")
                #LogToXBMC('Icon list item = %s' % selItem.getIconImage())


                if channelUid == '0':
                    self.showSimpleEpg()
                elif self.epg.has_key(channelUid):
                    self.showSimpleEpg(channelUid, icon)
                else:
                    self.showStatus('Загрузка программы')
                    thr = defines.MyThread(self.getEpg, {"uid": channelUid, "icon": icon})
                    thr.start()



    def checkButton(self, controlId):
        control = self.getControl(controlId)
        control.setLabel('>%s<' % control.getLabel())
        if self.seltab:
            btn = self.getControl(self.seltab)
            btn.setLabel(btn.getLabel().replace('<', '').replace('>',''))
        self.seltab = controlId
        LogToXBMC('Focused %s %s' % (WMainForm.CONTROL_LIST, self.selitem_id))
        if self.selitem_id > -1:
            #self.setFocusId(WMainForm.CONTROL_LIST)
            self.list.selectItem(self.selitem_id)

    def onClickCategory(self, controlId, categoryId):
        LogToXBMC("onClick button = %s category = %s" %(controlId, categoryId))
        print "filling channels"
        self.showStatus("Заполнение списка")
        if not self.list:
            print "self list is null"
            self.showStatus("Список не инициализирован")
            return
        self.list.reset()
        self.cur_category = categoryId
        print "current_category %s" % categoryId
        for ch in self.category[categoryId]:
            self.list.addItem(ch)
        self.hideStatus()
        if self.seltab != controlId:
            self.checkButton(controlId)
        if self.playditem > -1:
            self.setFocus(self.list)
            self.list.selectItem(self.playditem)
            self.playditem = -1

    def onClick(self, controlID):
        control = self.getControl(controlID)
        LogToXBMC('onClick %s' % controlID)
        if controlID == WMainForm.BTN_FAVORITES_CATEGORY_ID:
            self.onClickCategory(controlID, smotreshka.Smotreshka.FAVORITES_CATEGORY_ID)
        elif controlID == WMainForm.BTN_ALL_CHANNELS_CATEGORY_ID:
            self.onClickCategory(controlID, smotreshka.Smotreshka.ALL_CHANNELS_CATEGORY_ID)
        elif controlID == WMainForm.BTN_AIR_CATEGORY_ID:
            self.onClickCategory(controlID, smotreshka.Smotreshka.AIR_CATEGORY_ID)
        elif controlID == WMainForm.BTN_MOVIES_CATEGORY_ID:
            self.onClickCategory(controlID, smotreshka.Smotreshka.MOVIES_CATEGORY_ID)
        elif controlID == WMainForm.BTN_SPORT_CATEGORY_ID:
            self.onClickCategory(controlID, smotreshka.Smotreshka.SPORT_CATEGORY_ID)
        elif controlID == WMainForm.BTN_NEWS_CATEGORY_ID:
            self.onClickCategory(controlID, smotreshka.Smotreshka.NEWS_CATEGORY_ID)
        elif controlID == 200:
            self.setFocusId(50)
        elif controlID == 50:
            selItem = control.getSelectedItem()
            if not selItem:
                return

            print "clicked %s uid = %s" %(selItem.getLabel(), selItem.getProperty("channel_uid"))
            buf = xbmcgui.ListItem(selItem.getLabel())
            buf.setProperty("channel_uid", selItem.getProperty("channel_uid"))
            #buf.setProperty('icon', selItem.getProperty('icon'))
            buf.setProperty("type", selItem.getProperty("type"))
            buf.setProperty("id", selItem.getProperty("id"))
            if selItem.getProperty("type") == "archive":
                return
            self.playditem = self.selitem_id
            self.player.Start(buf)
            LogToXBMC("Stoped video");
            if xbmc.getCondVisibility("Window.IsVisible(home)"):
                LogToXBMC("Close from HOME Window")
                self.close()
            elif xbmc.getCondVisibility("Window.IsVisible(video)"):
                self.close();
                LogToXBMC("Is Video Window")
            elif xbmc.getCondVisibility("Window.IsVisible(programs)"):
                self.close();
                LogToXBMC("Is programs Window")
            elif xbmc.getCondVisibility("Window.IsVisible(addonbrowser)"):
                self.close();
                LogToXBMC("Is addonbrowser Window")
            elif xbmc.getCondVisibility("Window.IsVisible(12346)"):
                self.close();
                LogToXBMC("Is plugin Window")
            else:
                jrpc = json.loads(xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"GUI.GetProperties","params":{"properties":["currentwindow"]},"id":1}'))
                if jrpc["result"]["currentwindow"]["id"] == 10025:
                    LogToXBMC("Is video plugins window");
                    self.close();

                LogToXBMC("Is Other Window")


            LogToXBMC('CUR SELTAB %s' % self.seltab)

        # xbmc.executebuiltin('SendClick(12345,%s)' % self.seltab)
        elif controlID == WMainForm.BTN_FULLSCREEN:
            if defines.ADDON.getSetting("winmode") == "true":
                self.player.show()
            else:
                xbmc.executebuiltin("Action(FullScreen)")

        elif controlID == WMainForm.BTN_INFO:
            self.showInfoWindow()
            return



    def showSimpleEpg(self, epg_id = None, icon = None):
        controlEpg = self.getControl(WMainForm.LBL_FIRST_EPG)
        if epg_id and self.epg[epg_id].__len__() > 0:
            ctime = datetime.datetime.now()
            curepg = self.epg[epg_id][0]
            bt = curepg.startDate
            et = curepg.endDate
            percent = (ctime - bt).total_seconds()*100/((et-bt).total_seconds())
            self.progress.setPercent(percent)
            controlEpg.setLabel('%.2d:%.2d - %.2d:%.2d %s' % (bt.hour, bt.minute, et.hour, et.minute, curepg.title))
            nextepg = ''
            img = self.getControl(WMainForm.IMG_SCREEN)
            channel = smotreshka.Channel(uid=epg_id, title = None, thumbnail=icon)
            img.setImage(self.smApi.getThumbnailFileName(channel))
            for i in range(1,99):
                ce = None
                try:
                    ce = self.getControl(WMainForm.LBL_FIRST_EPG + i)
                except:
                    break
                if ce == None:
                    break
                if i >= self.epg[epg_id].__len__():
                    ce.setLabel('')
                else:
                    epg = self.epg[epg_id][i]
                    bt = epg.startDate
                    et = epg.endDate
                    ce.setLabel('%.2d:%.2d - %.2d:%.2d %s' % (bt.hour, bt.minute, et.hour, et.minute, epg.title))

        else:
            controlEpg.setLabel('Нет программы')
            for i in range(1,99):
                ce = None
                try:
                    self.getControl(WMainForm.LBL_FIRST_EPG + i).setLabel('');
                except:
                    break
            self.progress.setPercent(1)

    def onAction(self, action):
        if not action:
            super(WMainForm, self).onAction(action)
            return
        if action.getButtonCode() == 61513:
            return;
        if action in WMainForm.CANCEL_DIALOG:
            LogToXBMC('CLOSE FORM')
            self.isCanceled = True
            #xbmc.executebuiltin('Action(PreviousMenu)')
            self.close()
        elif action.getId() in WMainForm.ARROW_ACTIONS:
            LogToXBMC("ARROW_ACTION %s" % self.seltab )
            self.onFocus(self.getFocusId())
        elif action.getId() in WMainForm.CONTEXT_MENU_IDS and self.getFocusId() == WMainForm.CONTROL_LIST:
            return
        elif action.getId() == WMainForm.ACTION_MOUSE:
            if (self.getFocusId() == WMainForm.CONTROL_LIST):
                self.onFocus(WMainForm.CONTROL_LIST)
        else:
            super(WMainForm, self).onAction(action)

    def updateList(self):
        self.showStatus("Получение списка каналов")
        self.list = self.getControl(50)
        self.initLists()
        thr = defines.MyThread(self.getChannels, 'channel', True)
        thr.daemon = False
        thr.start()
        LogToXBMC('Ожидание результата')
        thr.join(10)
        self.list.reset()
        self.setFocus(self.getControl(WMainForm.BTN_FAVORITES_CATEGORY_ID))
        self.img_progress.setVisible(False)
        self.hideStatus()
        LogToXBMC(self.selitem_id)


    def showStatus(self, str):
        if self.img_progress: self.img_progress.setVisible(True)
        if self.txt_progress: self.txt_progress.setLabel(str)
        if self.infoform: self.infoform.printASStatus(str)

    def showInfoStatus(self, str):
        if self.infoform: self.infoform.printASStatus(str)

    def hideStatus(self):
        if self.img_progress: self.img_progress.setVisible(False)
        if self.txt_progress: self.txt_progress.setLabel("")

    def fillChannels(self):
        print "filling channels"
        self.showStatus("Заполнение списка")
        if not self.list:
            print "self list is null"
            self.showStatus("Список не инициализирован")
            return
        self.list.reset()
        print "current_category %s" % self.cur_category
        print "channels %s" % self.category[self.cur_category]["channels"]
        if self.category[self.cur_category]["channels"] == 0:
            self.fillCategory()
            self.hideStatus()
        else:
            li = xbmcgui.ListItem('..')
            self.list.addItem(li)
            for ch in self.category[self.cur_category]["channels"]:
                self.list.addItem(ch)
            self.hideStatus()

    def fillCategory(self):
        if not self.list:
            self.showStatus("Список не инициализирован")
            return
        self.list.reset()
        for gr in self.category:
            li = xbmcgui.ListItem(self.category[gr]["name"])
            li.setProperty('type', 'category')
            li.setProperty('id', '%s' % gr)
            self.list.addItem(li)


    def IsCanceled(self):
        return self.isCanceled