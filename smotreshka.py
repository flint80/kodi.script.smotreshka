# -*- coding: utf-8 -*-
import urllib
import urllib2
import os
import datetime
import json
import cookielib
import time
import requests


class Channel:

    def __init__(self, uid, title, thumbnail):
        self.uid = uid
        self.title = title
        self.thumbnail = thumbnail



class Epg:
    def __init__(self, title, description, start_date, end_date):
        self.title = title
        self.description = description
        self.startDate = start_date;
        self.endDate = end_date;



class Smotreshka:

    NEWS_CATEGORY_ID = 1
    MOVIES_CATEGORY_ID = 2
    SPORT_CATEGORY_ID = 3
    AIR_CATEGORY_ID = 4
    FAVORITES_CATEGORY_ID = 5
    ALL_CHANNELS_CATEGORY_ID = 6
    ENTERTAINMENT_CATEGORY_ID = 7
    SCIENCE_CATEGORY_ID=8


    def __init__(self, email, password, dataDir):
        self._email = email
        self._password = password
        self._dataDir = dataDir
        self._cookies = None
        self._userAgent = "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0"
        self._categoriesMap = {u'новости':Smotreshka.NEWS_CATEGORY_ID,
                               u'Новости':Smotreshka.NEWS_CATEGORY_ID,
                               u'кино':Smotreshka.MOVIES_CATEGORY_ID,
                               u'Кино':Smotreshka.MOVIES_CATEGORY_ID,
                               u'спорт':Smotreshka.SPORT_CATEGORY_ID,
                               u'Развлекательные':Smotreshka.ENTERTAINMENT_CATEGORY_ID,
                               u'Развлекательный':Smotreshka.ENTERTAINMENT_CATEGORY_ID,
                               u'развлечения':Smotreshka.ENTERTAINMENT_CATEGORY_ID,
                               u'познавательные':Smotreshka.SCIENCE_CATEGORY_ID,
                               u'Познавательные':Smotreshka.SCIENCE_CATEGORY_ID,
                               u'Познавательный':Smotreshka.SCIENCE_CATEGORY_ID,
                               u'Спорт':Smotreshka.SPORT_CATEGORY_ID,
                               u'Эфирные':Smotreshka.AIR_CATEGORY_ID,
                               u'Эфирный':Smotreshka.AIR_CATEGORY_ID,
                               u'основные':Smotreshka.AIR_CATEGORY_ID}
        self._channels_cache = None
        self._channels_last_update = None

    def _delta_in_hours(self, filename):
        timestamp = os.path.getmtime(filename)
        mod_time = datetime.datetime.fromtimestamp(timestamp)
        delta = datetime.datetime.now() - mod_time
        return delta.total_seconds() // 3600

    def check(self):
        try:
            return self._login()
        except:
            return False

    def _login(self):
        file_name = self._dataDir + "/cookie"
        if os.path.exists(file_name):
            if self._delta_in_hours(file_name) < 20:
                f = open(file_name, 'r')
                self._cookies = f.read()
                print "cookie loaded from disk"
                return True
        cookies2 = cookielib.LWPCookieJar()
        handlers = [
            urllib2.HTTPHandler(),
            urllib2.HTTPSHandler(),
            urllib2.HTTPCookieProcessor(cookies2)
        ]
        opener = urllib2.build_opener(*handlers)
        url = 'http://fe.smotreshka.tv/login'
        values = {'email': self._email, 'password': self._password}
        data = urllib.urlencode(values)
        req = urllib2.Request(url)
        req.add_header('User-Agent', self._userAgent)
        req.add_data(data)
        response = opener.open(req)
        if response.code != 200:
            print "cookie not loaded"
            return False

        self._cookies = None
        for cookie in cookies2:
            if self._cookies is not None:
                self._cookies = self._cookies + ";" + cookie.name + "=" + cookie.value
            else:
                self._cookies = cookie.name + "=" + cookie.value

        if not os.path.exists(os.path.dirname(file_name)):
            os.makedirs(os.path.dirname(file_name))

        f = open(file_name, 'w')
        f.write(self._cookies)
        print "cookie saved to file"
        return True

    def get_channels(self):
        if self._channels_last_update:
            delta = datetime.datetime.now() - self._channels_last_update
            if delta.total_seconds() < 3600:
                return self._channels_cache

        file_name = self._dataDir + "/channels"
        channels_json = None
        if os.path.exists(file_name):
            if self._delta_in_hours(file_name) < 5:
                f = open(file_name, 'r')
                channels_json = json.loads(f.read())

        if not channels_json:
            self._login()
            url = 'http://fe.smotreshka.tv/channels'
            req = urllib2.Request(url)
            req.add_header('User-Agent', self._userAgent)
            req.add_header('Cookie', self._cookies);
            response = urllib2.urlopen(req)
            body = response.read()
            if not os.path.exists(os.path.dirname(file_name)):
                os.makedirs(os.path.dirname(file_name))

            f = open(file_name, 'w')
            f.write(body)
            channels_json = json.loads(body)

        favorites = []
        file_name = self._dataDir + "/account"
        account_json = None

        if os.path.exists(file_name):
            if self._delta_in_hours(file_name) < 1:
                f = open(file_name, 'r')
                account_json = json.loads(f.read())

        if not account_json:
            self._login()
            url = 'http://fe.smotreshka.tv/v2/account'
            req = urllib2.Request(url)
            req.add_header('User-Agent', self._userAgent)
            req.add_header('Cookie', self._cookies);
            response = urllib2.urlopen(req)
            body = response.read()
            account_json = json.loads(body)
            if not os.path.exists(os.path.dirname(file_name)):
                os.makedirs(os.path.dirname(file_name))

            f = open(file_name, 'w')
            f.write(body)

        if 'profile' in account_json:
            if 'favorites' in account_json['profile']:
                for favorite in account_json['profile']['favorites']:
                    favorites = favorites+[favorite]

        categories_dict = {}
        if "channels" in channels_json:
            for channel_json in channels_json['channels']:
                if "info" in channel_json:
                    info = channel_json["info"]
                    if 'purchaseInfo' in info:
                        purchase_info = info['purchaseInfo'];
                        if 'bought' in purchase_info:
                            if purchase_info['bought']:
                                thumbnail = None;
                                if 'mediaInfo' in info:
                                    if 'thumbnails' in info['mediaInfo']:
                                        thumbnails = info['mediaInfo']['thumbnails']
                                        if len(thumbnails) > 0:
                                            thumbnail = thumbnails[0]['url']
                                channel_id = channel_json['id']
                                channel_title = None
                                categories = [Smotreshka.ALL_CHANNELS_CATEGORY_ID]
                                if channel_id in favorites:
                                    categories = categories+[Smotreshka.FAVORITES_CATEGORY_ID]
                                if 'metaInfo' in info:
                                    if 'title' in info['metaInfo']:
                                        channel_title = info["metaInfo"]['title']
                                    if 'genres' in info['metaInfo']:
                                        for genre in info['metaInfo']['genres']:
                                            if genre in self._categoriesMap:
                                                category_id = self._categoriesMap[genre]
                                                if category_id not in categories:
                                                    categories = categories+[category_id]

                                if channel_id and channel_title:
                                    channel = Channel(channel_id, channel_title, thumbnail)
                                    for category_id in categories:
                                        if category_id not in categories_dict:
                                            categories_dict[category_id] = []
                                        categories_dict[category_id]= categories_dict[category_id]+[channel]

        for category_id in categories_dict:
            channels = categories_dict[category_id]
            channels.sort(key=lambda ch: ch.title)
        self._channels_cache = categories_dict
        self._channels_last_update = datetime.datetime.now()
        return categories_dict

    def get_play_url(self, channel_id):
        print 'getting url for channel %s' % channel_id
        file_name = self._dataDir + "/playback/" + channel_id
        playback_info = None
        if os.path.exists(file_name):
            if self._delta_in_hours(file_name) < 5:
                f = open(file_name, 'r')
                playback_info = json.loads(f.read())
        if not playback_info:
            self._login()
            url = 'http://fe.smotreshka.tv/playback-info/' + channel_id
            print "url is %s" % url
            req = urllib2.Request(url)
            req.add_header('User-Agent', self._userAgent)
            req.add_header('Cookie', self._cookies);
            response = urllib2.urlopen(req)
            body = response.read()
            if not os.path.exists(os.path.dirname(file_name)):
                os.makedirs(os.path.dirname(file_name))

            f = open(file_name, 'w')
            f.write(body)
            playback_info = json.loads(body)
        if 'languages' in playback_info:
            languages = playback_info['languages']
            if len(languages) > 0:
                language = playback_info['languages'][0]
                if 'renditions' in language:
                    for rend in language['renditions']:
                        if rend['id'] == "1m":
                            return rend['url']
                    for rend in language['renditions']:
                        if rend['id'] == "Auto":
                            return rend['url']

    def get_epg(self, channel_id):
        file_name = self._dataDir + "/epg/" + channel_id
        epg_info = None
        if os.path.exists(file_name):
            if self._delta_in_hours(file_name) < 2:
                f = open(file_name, 'r')
                epg_info = json.loads(f.read())
        start = datetime.datetime.now()
        end = start + datetime.timedelta(hours=5)
        if not epg_info:
            self._login()
            url = 'http://fe.smotreshka.tv/channels/' + channel_id + "/programs?period=%d:%d" % (time.mktime((start - datetime.timedelta(hours=4)).timetuple()), time.mktime(end.timetuple()))
            req = urllib2.Request(url)
            req.add_header('User-Agent', self._userAgent)
            req.add_header('Cookie', self._cookies)
            response = urllib2.urlopen(req)
            body = response.read()
            if not os.path.exists(os.path.dirname(file_name)):
                os.makedirs(os.path.dirname(file_name))

            f = open(file_name, 'w')
            f.write(body)
            epg_info = json.loads(body)
        result = []
        if 'programs' in epg_info:
            for epg in epg_info['programs']:
                if 'scheduleInfo' in epg:
                    schedule_info = epg['scheduleInfo']
                    epg_end = None
                    epg_start = None
                    if 'start' in schedule_info:
                        epg_start = datetime.datetime.fromtimestamp(epg['scheduleInfo']['start'])
                    if 'end' in schedule_info:
                        epg_end = datetime.datetime.fromtimestamp(epg['scheduleInfo']['end'])
                        if epg_end > start:
                            result = result + [Epg(epg['metaInfo']['title'], epg['metaInfo']['title'], epg_start, epg_end)]
        return result



    def getThumbnailFileName(self, channel):
        file_name = self._dataDir+"/thumbnails/"+channel.uid+".jpg"
        if os.path.exists(file_name):
            return file_name
        self._login()
        url = channel.thumbnail
        if not url:
            url  = "https://d1nhio0ox7pgb.cloudfront.net/_img/v_collection_png/64x64/shadow/unknown.png"
        try:
            if not os.path.exists(os.path.dirname(file_name)):
                os.makedirs(os.path.dirname(file_name))
            f = open(file_name,'wb')
            headers = {'User-Agent':self._userAgent, 'Cookie':self._cookies}
            content = requests.get(url, headers=headers).content
            f.write(content)
            f.close()
            return file_name
        except:
            return None

