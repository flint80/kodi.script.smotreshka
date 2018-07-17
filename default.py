# -*- coding: utf-8 -*-

import utils

import smotreshka

import mainform

if __name__ == '__main__':

    login = utils.getSetting("login")
    password = utils.getSetting("password")
    if (not login) or (not password):
        utils.showMessage("не заданы параметры подключения к сервису")
    else:
        sm = smotreshka.Smotreshka(login, password, utils.DATA_PATH)
        if not sm.check():
            utils.showMessage("не удается подключиться к сервису, проверьте логин и пароль")
        else:
            utils.showMessage("запускаем приложение")
            w = mainform.WMainForm("mainform.xml", utils.ADDON_PATH, "flinty")
            w.smApi = sm
            w.doModal()
            del w
