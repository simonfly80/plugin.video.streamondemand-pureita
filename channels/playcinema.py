# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand.- XBMC Plugin
# Canal para playcinema
# http://blog.tvalacarta.info/plugin-xbmc/streamondemand.
# ------------------------------------------------------------
import re
import sys
import urllib2
import urlparse

from core import config
from core import logger
from core import scrapertools
from core.item import Item

__channel__ = "playcinema"
__category__ = "F"
__type__ = "generic"
__title__ = "playcinema.org (IT)"
__language__ = "IT"

DEBUG = config.get_setting("debug")

host = "http://www.playcinema.org"

headers = [
    ['User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:39.0) Gecko/20100101 Firefox/39.0'],
    ['Accept-Encoding', 'gzip, deflate']
]


def isGeneric():
    return True


def mainlist(item):
    logger.info("streamondemand.playcinema mainlist")
    itemlist = [Item(channel=__channel__,
                     title="[COLOR azure]Ultimi Film Inseriti[/COLOR]",
                     action="peliculas",
                     url=host,
                     thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Film Per Categoria[/COLOR]",
                     action="categorias",
                     url=host,
                     thumbnail="http://xbmc-repo-ackbarr.googlecode.com/svn/trunk/dev/skin.cirrus%20extended%20v2/extras/moviegenres/All%20Movies%20by%20Genre.png"),
                Item(channel=__channel__,
                     title="[COLOR yellow]Cerca...[/COLOR]",
                     action="search",
                     thumbnail="http://dc467.4shared.com/img/fEbJqOum/s7/13feaf0c8c0/Search")]

    return itemlist


def categorias(item):
    itemlist = []

    # Descarga la pagina
    data = anti_cloudflare(item.url)

    patron = '<ul class="sub-menu">(.*?)</ul>'
    bloque = scrapertools.find_single_match(data, patron)

    # Extrae las entradas (carpetas)
    patron = '<li[^>]+><a href="([^"]+)">(.*?)</a></li>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for scrapedurl, scrapedtitle in matches:
        if (DEBUG): logger.info("title=[" + scrapedtitle + "], url=[" + scrapedurl + "]")
        itemlist.append(
                Item(channel=__channel__,
                     action="peliculas",
                     title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                     url=scrapedurl,
                     thumbnail="http://xbmc-repo-ackbarr.googlecode.com/svn/trunk/dev/skin.cirrus%20extended%20v2/extras/moviegenres/All%20Movies%20by%20Genre.png",
                     folder=True))

    return itemlist


def search(item, texto):
    logger.info("[playcinema.py] " + item.url + " search " + texto)
    item.url = host + "/?s=" + texto
    try:
        return peliculas(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def peliculas(item):
    logger.info("streamondemand.playcinema peliculas")
    itemlist = []

    data = anti_cloudflare(item.url)

    # ------------------------------------------------
    cookies = ""
    matches = re.compile('(.playcinema.org.*?)\n', re.DOTALL).findall(config.get_cookie_data())
    for cookie in matches:
        name = cookie.split('\t')[5]
        value = cookie.split('\t')[6]
        cookies += name + "=" + value + ";"
    headers.append(['Cookie', cookies[:-1]])
    import urllib
    _headers = urllib.urlencode(dict(headers))
    # ------------------------------------------------

    # Extrae las entradas (carpetas)
    patron = '<div class="moviefilm">\s*'
    patron += '<a href="([^"]+)">\s*'
    patron += '<img src="([^"]+)" alt="([^"]+)"[^>]+></a>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedthumbnail, scrapedtitle in matches:
        # response = urllib2.urlopen(scrapedurl)
        # html = response.read()
        # start = html.find("<div class=\"filmicerik\">")
        # start = html.find("<p><span style=\"font-family: Arial, Helvetica, sans-serif;\">")
        # end = html.find("<span style=\"font-size: xx-small;\">+Info", start)
        # end = html.find("</font></a><br />", start)
        # scrapedplot = html[start:end]
        # scrapedplot = re.sub(r'<[^>]*>', '', scrapedplot)
        # scrapedplot = scrapertools.decodeHtmlentities(scrapedplot)
        scrapedplot = ""
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle.replace("Streaming", ""))
        scrapedthumbnail += '|' + _headers
        if (DEBUG): logger.info(
                "title=[" + scrapedtitle + "], url=[" + scrapedurl + "], thumbnail=[" + scrapedthumbnail + "]")
        tmdbtitle = scrapedtitle.split("(")[0]
        try:
           plot, fanart, poster, extrameta = info(tmdbtitle)

           itemlist.append(
               Item(channel=__channel__,
                    thumbnail=poster,
                    fanart=fanart if fanart != "" else poster,
                    extrameta=extrameta,
                    plot=str(plot),
                    action="findvideos",
                    title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                    url=scrapedurl,
                    fulltitle=scrapedtitle,
                    show=scrapedtitle,
                    folder=True))
        except:
           itemlist.append(
               Item(channel=__channel__,
                    action="findvideos",
                    fulltitle=scrapedtitle,
                    show=scrapedtitle,
                    title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                    url=scrapedurl,
                    thumbnail=scrapedthumbnail,
                    plot=scrapedplot,
                    folder=True))

    # Extrae el paginador
    patronvideos = '<a class="nextpostslink" rel="next" href="([^"]+)">&raquo;</a>'
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    if len(matches) > 0:
        scrapedurl = urlparse.urljoin(item.url, matches[0])
        itemlist.append(
            Item(channel=__channel__,
                 action="HomePage",
                 title="[COLOR yellow]Torna Home[/COLOR]",
                 folder=True)),
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR orange]Successivo >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png",
                 folder=True))

    return itemlist

def HomePage(item):
    import xbmc
    xbmc.executebuiltin("ReplaceWindow(10024,plugin://plugin.video.streamondemand-pureita)")

def anti_cloudflare(url):
    # global headers

    try:
        resp_headers = scrapertools.get_headers_from_response(url, headers=headers)
        resp_headers = dict(resp_headers)
    except urllib2.HTTPError, e:
        resp_headers = e.headers

    if 'refresh' in resp_headers:
        import time
        time.sleep(int(resp_headers['refresh'][:1]))

        scrapertools.get_headers_from_response(host + "/" + resp_headers['refresh'][7:], headers=headers)

    return scrapertools.cache_page(url, headers=headers)

def info(title):
    logger.info("streamondemand.playcinema info")
    try:
        from core.tmdb import Tmdb
        oTmdb= Tmdb(texto_buscado=title, tipo= "movie", include_adult="true", idioma_busqueda="it")
        count = 0
        if oTmdb.total_results > 0:
           extrameta = {}
           extrameta["Year"] = oTmdb.result["release_date"][:4]
           extrameta["Genre"] = ", ".join(oTmdb.result["genres"])
           extrameta["Rating"] = float(oTmdb.result["vote_average"])
           fanart=oTmdb.get_backdrop()
           poster=oTmdb.get_poster()
           plot=oTmdb.get_sinopsis()
           return plot, fanart, poster, extrameta
    except:
        pass
