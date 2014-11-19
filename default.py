import urllib
import urllib2
import re
import os
import xbmcplugin
import xbmcgui
import xbmcaddon
import sys
from bs4 import BeautifulSoup

addon = xbmcaddon.Addon(id='plugin.video.tmc-zeetv-master')
addon_version = addon.getAddonInfo('version')
debug = addon.getSetting('debug')
base_url = 'http://www.zeetv.com/'

def addon_log(string):
    if debug == 'true':
        xbmc.log("[plugin.video.tmc-zeetv-master-%s]: %s" %(addon_version, string))

def make_request(url):
    addon_log('Request URL: ' + url)
    try:
        headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:32.0) Gecko/20100101 Firefox/32.0', 'Accept' : 'text/html,application/xml', 'Referer' : base_url}
        req = urllib2.Request(url,None,headers)
        response = urllib2.urlopen(req)
        data = response.read()
        addon_log('ResponseInfo: %s' %response.info())
        response.close()
        return data
    except urllib2.URLError, e:
        addon_log('Failed to Open: "%s"' %url)
        if hasattr(e, 'reason'):
            addon_log('Reason: %s' %e.reason)
        if hasattr(e, 'code'):
            addon_log('Code: %s' %e.code)

def get_shows():
    addon_log('get_shows: begin...')

    html = make_request(base_url + 'shows/')
    soup = BeautifulSoup(html)

    tag_showlist = soup.find('div', attrs={"class" : "list_carousel responsive"})
    tags_show = tag_showlist.findAll('a')
    for tag_show in tags_show:
        tag_play = tag_show.find('div', attrs={"class" : "play-btn"})
        if tag_play:
            item = tag_show['title']
            link = tag_show['href']
            img = tag_show.img['src']

            link = link + 'video/'

            addDir(1, item, link, img, False)

    addon_log('get_shows: end...')

def get_episodes():
    addon_log('get_episodes: begin...')

    html = make_request(url)
    soup = BeautifulSoup(html)

    tag_episodelist = soup.find('ul', attrs={"id" : "showv_list"})
    tags_episode = tag_episodelist.findAll('a')
    for tag_episode in tags_episode:
        tag_play = tag_episode.find('div', attrs={"class" : "play-btn"})
        if tag_play:
            item = tag_episode['title']
            link = tag_episode['href']
            img = tag_episode.img['src']

            addDir(11, item, link, img, True)

    tag_next = soup.find('div', attrs={"class" : "pagination"})
    if tag_next:
        tag_next = tag_next.findAll('a')
        if tag_next:
            tag_next = tag_next[-1]
            next = tag_next['href']
            if -1 == next.find('javascript:void(0)'):
                addDir(1, 'Next Page...', next, '')

    addon_log('get_episodes: end...')

def get_video_url():
    addon_log('get_video_url: begin...')

    quality = addon.getSetting('quality')
    addon_log('Video Quality: ' + quality)

    link = ''

    html = make_request(url)

    matchlist = re.compile("'(http://dittotv.[^']*.mp4[^']*)'").findall(html)
    if matchlist:
        for match in matchlist:
            if ('Computer' == quality) and (-1 != match.find(".m3u8")):
                link = match
            elif ('Android' == quality):
                link = match

    item = xbmcgui.ListItem(path=link)
    xbmcplugin.setResolvedUrl(handle=int(sys.argv[1]), succeeded=('' != link), listitem=item)

    addon_log('get_video_url: end...')

    return link


def addDir(mode,name,url,image,isplayable=False):
    name = name.encode('ascii', 'ignore')
    url = url.encode('ascii', 'ignore')
    image = image.encode('ascii', 'ignore')

    if 0==mode:
        link = url
    else:
        link = sys.argv[0]+"?mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&url="+urllib.quote_plus(url)

    ok=True
    item=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=image)
    item.setInfo( type="Video", infoLabels={ "Title": name } )
    isfolder=True
    if isplayable:
        item.setProperty('IsPlayable', 'true')
        isfolder=False
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=link,listitem=item,isFolder=isfolder)
    return ok

def get_params():
    param=[]
    paramstring=sys.argv[2]
    if len(paramstring)>=2:
        params=sys.argv[2]
        cleanedparams=params.replace('?','')
        if (params[len(params)-1]=='/'):
            params=params[0:len(params)-2]
        pairsofparams=cleanedparams.split('&')
        param={}
        for i in range(len(pairsofparams)):
            splitparams={}
            splitparams=pairsofparams[i].split('=')
            if (len(splitparams))==2:
                param[splitparams[0]]=splitparams[1]
    return param

params=get_params()
url=None
name=None
mode=None

try:
    mode=int(params["mode"])
except:
    pass
try:
    name=urllib.unquote_plus(params["name"])
except:
    pass
try:
    url=urllib.unquote_plus(params["url"])
except:
    pass

addon_log("Mode: "+str(mode))
addon_log("Name: "+str(name))
addon_log("URL: "+str(url))

if mode==None:
    get_shows()

if mode==1:
    get_episodes()

if mode==11:
    get_video_url()

xbmcplugin.endOfDirectory(int(sys.argv[1]))
