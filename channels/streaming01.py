# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand.- XBMC Plugin
# Canal para piratestreaming
# http://blog.tvalacarta.info/plugin-xbmc/streamondemand.
# ------------------------------------------------------------
import re
import sys
import urlparse

from core import config
from core import logger
from core import scrapertools
from core.item import Item

__channel__ = "streaming01"
__category__ = "F"
__type__ = "generic"
__title__ = "Streaming01.com (IT)"
__language__ = "IT"

DEBUG = config.get_setting("debug")

host = "http://www.streaming01.com"


def isGeneric():
    return True


def mainlist(item):
    logger.info("streamondemand.streaming01 mainlist")
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
    data = scrapertools.cache_page(item.url)

    patron = '<ul class="main-menu clearfix">(.*?)</ul>'
    bloque = scrapertools.find_single_match(data, patron)

    # Extrae las entradas (carpetas)
    patron = '<li><a href="([^"]+)">(.*?)</a></li>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for scrapedurl, scrapedtitle in matches:
        if (DEBUG): logger.info("title=[" + scrapedtitle + "], url=[" + scrapedurl + "]")
        itemlist.append(
                Item(channel=__channel__,
                     action="peliculas",
                     title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                     url=host + scrapedurl,
                     thumbnail="http://xbmc-repo-ackbarr.googlecode.com/svn/trunk/dev/skin.cirrus%20extended%20v2/extras/moviegenres/All%20Movies%20by%20Genre.png",
                     folder=True))

    return itemlist


def search(item, texto):
    logger.info("[streaming01.py] " + item.url + " search " + texto)
    item.url = host + "/index.php?do=search&subaction=search&story=" + texto
    try:
        return peliculas(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def peliculas(item):
    logger.info("streamondemand.streaming01 peliculas")
    itemlist = []

    # Descarga la pagina
    data = scrapertools.cache_page(item.url)

    # Extrae las entradas (carpetas)
    patron = '<a class="short-img" href="([^"]+)"[^>]+>\s*'
    patron += '<img src="([^"]+)"[^>]+>\s*'
    patron += '</a>\s*'
    patron += '<div[^>]+>\s*'
    patron += '<h3>[^>]+>(.*?)</a>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedthumbnail, scrapedtitle in matches:
 #		COMMENTING PLOT LINES BECAUSE CHANNELS' TOO SLOW
 #       html = scrapertools.cache_page(scrapedurl)
 #       start = html.find("<div class=\"full-text clearfix desc-text\">")
 #       end = html.find("<table>", start)
 #       scrapedplot = html[start:end]
 #       scrapedplot = re.sub(r'<.*?>', '', scrapedplot)
 #       scrapedplot = scrapertools.decodeHtmlentities(scrapedplot)
        scrapedtitle = scrapedtitle.replace("Streaming ", "")
        scrapedtitle = scrapedtitle.replace(" e download", "")
        scrapedtitle = scrapedtitle.replace("gratis", "")
        scrapedtitle = scrapedtitle.replace("streaming", "")
        scrapedtitle = scrapedtitle.replace("ita", "")
        scrapedtitle = scrapedtitle.replace("ITA", "")
        scrapedtitle = scrapedtitle.replace("download", "")
        scrapedtitle = scrapedtitle.replace("GRATIS", "")
        scrapedtitle = scrapedtitle.replace("[", "")
        scrapedtitle = scrapedtitle.replace("]", "")
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        if DEBUG: logger.info(
                "title=[" + scrapedtitle + "], url=[" + scrapedurl + "], thumbnail=[" + scrapedthumbnail + "]")
        itemlist.append(
                Item(channel=__channel__,
                     action="findvideos",
                     fulltitle=scrapedtitle,
                     show=scrapedtitle,
                     title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                     url=scrapedurl,
                     thumbnail=scrapedthumbnail,
                     folder=True))

    # Extrae el paginador
    patronvideos = '<span class="pnext"><a href="([^"]+)">Avanti</a></span>'
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


