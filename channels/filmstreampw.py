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
from servers import servertools

__channel__ = "filmstreampw"
__category__ = "F,S"
__type__ = "generic"
__title__ = "Fimstream.pw (IT)"
__language__ = "IT"

headers = [
    ['User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:38.0) Gecko/20100101 Firefox/38.0'],
    ['Accept-Encoding', 'gzip, deflate']
]

host = 'http://filmstream.re/'

DEBUG = config.get_setting("debug")


def isGeneric():
    return True


def mainlist(item):
    logger.info("streamondemand.filmstreampw mainlist")
    itemlist = [Item(channel=__channel__,
                     title="[COLOR azure]Ultimi Film Inseriti[/COLOR]",
                     action="peliculas",
                     url=host + "film/",
                     thumbnail="http://dc584.4shared.com/img/XImgcB94/s7/13feaf0b538/saquinho_de_pipoca_01"),
                Item(channel=__channel__,
                     title="[COLOR azure]Film Per Genere[/COLOR]",
                     action="categorias",
                     url=host,
                     thumbnail="http://xbmc-repo-ackbarr.googlecode.com/svn/trunk/dev/skin.cirrus%20extended%20v2/extras/moviegenres/All%20Movies%20by%20Genre.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Film e Serie per anno[/COLOR]",
                     action="byyear",
                     url=host,
                     thumbnail="http://xbmc-repo-ackbarr.googlecode.com/svn/trunk/dev/skin.cirrus%20extended%20v2/extras/moviegenres/Movie%20Year.png"),
                Item(channel=__channel__,
                     title="[COLOR yellow]Cerca...[/COLOR]",
                     action="search",
                     thumbnail="http://dc467.4shared.com/img/fEbJqOum/s7/13feaf0c8c0/Search"),
                Item(channel=__channel__,
                     title="[COLOR azure]Serie TV[/COLOR]",
                     extra="serie",
                     action="peliculas",
                     url=host + "serie-tv/",
                     thumbnail="http://xbmc-repo-ackbarr.googlecode.com/svn/trunk/dev/skin.cirrus%20extended%20v2/extras/moviegenres/New%20TV%20Shows.png"),
                Item(channel=__channel__,
                     title="[COLOR yellow]Cerca Serie TV...[/COLOR]",
                     action="search",
                     extra="serie",
                     thumbnail="http://dc467.4shared.com/img/fEbJqOum/s7/13feaf0c8c0/Search")]
    return itemlist


def categorias(item):
    logger.info("streamondemand.filmstreampw categorias")
    itemlist = []

    data = scrapertools.cache_page(item.url, headers=headers)

    # Narrow search by selecting only the combo
    patron = '<ul class="box-bg right-navi clearfix">([^?]+)</select>'
    bloque = scrapertools.get_match(data, patron)

    # The categories are the options for the combo
    patron = '<li><a href="([^"]+)">(.*?)</a></li>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for scrapedurl, scrapedtitle in matches:
        scrapedurl = urlparse.urljoin(item.url, scrapedurl)
        scrapedthumbnail = ""
        scrapedplot = ""
        if (DEBUG): logger.info(
                "title=[" + scrapedtitle + "], url=[" + scrapedurl + "], thumbnail=[" + scrapedthumbnail + "]")
        itemlist.append(
                Item(channel=__channel__,
                     action="peliculas",
                     title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                     url=scrapedurl,
                     thumbnail=scrapedthumbnail,
                     plot=scrapedplot))

    return itemlist


def byyear(item):
    logger.info("streamondemand.filmstreampw byyear")
    itemlist = []

    data = scrapertools.cache_page(item.url, headers=headers)

    # Narrow search by selecting only the combo
    patron = '<ul class="box-bg right-navi clearfix">([^?]+)</select>'
    bloque = scrapertools.get_match(data, patron)

    # The categories are the options for the combo
    patron = '<option value="([^"]+)">(.*?)</option>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for scrapedurl, scrapedtitle in matches:
        scrapedurl = urlparse.urljoin(item.url, scrapedurl)
        scrapedthumbnail = ""
        scrapedplot = ""
        if (DEBUG): logger.info(
                "title=[" + scrapedtitle + "], url=[" + scrapedurl + "], thumbnail=[" + scrapedthumbnail + "]")
        itemlist.append(
                Item(channel=__channel__,
                     action="peliculas",
                     title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                     url=scrapedurl,
                     thumbnail=scrapedthumbnail,
                     plot=scrapedplot))

    return itemlist


def search(item, texto):
    logger.info("[filmstreampw.py] " + item.url + " search " + texto)
    item.url = host + "index.php?do=search&subaction=search&story=" + texto
    try:
        return peliculasx(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return [] 


def peliculasx(item):
    logger.info("streamondemand.filmstreampw peliculas")
    itemlist = []

    # Descarga la pagina
    data = scrapertools.cache_page(item.url, headers=headers)

    # Extrae las entradas (carpetas)
    patron = '<div class="news2 float">.*?<div class="boxgrid2 caption2">.*?<a href="([^"]+)">.*?<img.*?src="([^"]+)"/>.*?<div class="cover2 boxcaption2">.*?<div class="boxgridtext">(.*?)</div>.*?<br>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedthumbnail, scrapedtitle in matches:
        html = scrapertools.cache_page(scrapedurl, headers=headers)
        start = html.find("<li class=\"current\" style=\"font-size: 15px; line-height: 18px;\">")
        end = html.find("</div></li>", start)
        scrapedplot = html[start:end]
        scrapedplot = re.sub(r'<[^>]*>', '', scrapedplot)
        scrapedplot = scrapertools.decodeHtmlentities(scrapedplot)
        scrapedtitle = scrapedtitle.strip()
        if (DEBUG): logger.info(
                "title=[" + scrapedtitle + "], url=[" + scrapedurl + "], thumbnail=[" + scrapedthumbnail + "]")
        itemlist.append(
                Item(channel=__channel__,
                     action="episodios" if item.extra == "serie" else "findvideos",
                     fulltitle=scrapedtitle,
                     show=scrapedtitle,
                     title=scrapedtitle,
                     url=scrapedurl,
                     thumbnail=scrapedthumbnail,
                     plot=scrapedplot,
                     folder=True,
                     fanart=scrapedthumbnail))

    return itemlist


def peliculas(item):
    logger.info("streamondemand.filmstreampw peliculas")
    itemlist = []

    # Descarga la pagina
    data = scrapertools.cache_page(item.url, headers=headers)

    # Extrae las entradas (carpetas)
    patron = '<div class="boxgrid2[^>]+>[^<]+<a href="([^"]+)">[^<]+<img.*?[^"]+"[^"]+" src="([^"]+)"[^>]+>[^>]+>[^>]+>([^<]+)<br>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedthumbnail, scrapedtitle in matches:
        html = scrapertools.cache_page(scrapedurl, headers=headers)
        start = html.find("<li class=\"current\" style=\"font-size: 15px; line-height: 18px;\">")
        end = html.find("<p><i></i></p></li>", start)
        scrapedplot = html[start:end]
        scrapedplot = re.sub(r'<[^>]*>', '', scrapedplot)
        scrapedtitle = scrapedtitle.strip()
        if (DEBUG): logger.info(
                "title=[" + scrapedtitle + "], url=[" + scrapedurl + "], thumbnail=[" + scrapedthumbnail + "]")
        tmdbtitle1 = scrapedtitle.split("[")[0]
        tmdbtitle = tmdbtitle1.split("(")[0]
        try:
           plot, fanart, poster, extrameta = info(tmdbtitle)

           itemlist.append(
               Item(channel=__channel__,
                    thumbnail=poster,
                    fanart=fanart if fanart != "" else poster,
                    extrameta=extrameta,
                    plot=str(plot),
                    action="episodios" if item.extra == "serie" else "findvideos",
                    title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                    url=scrapedurl,
                    fulltitle=scrapedtitle,
                    show=scrapedtitle,
                    folder=True))
        except:
           itemlist.append(
               Item(channel=__channel__,
                    action="episodios" if item.extra == "serie" else "findvideos",
                    fulltitle=scrapedtitle,
                    show=scrapedtitle,
                    title=scrapedtitle,
                    url=scrapedurl,
                    thumbnail=scrapedthumbnail,
                    plot=scrapedplot,
                    folder=True))

    # Extrae el paginador
    patronvideos = '<a href="([^"]+)">Avanti</a>'
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

def episodios(item):
    logger.info("streamondemand.channels.filmstreampw episodios")

    itemlist = []

    data = scrapertools.cache_page(item.url, headers=headers)

    post_url = host + 'engine/ajax/a.sseries.php'
    serie_id = scrapertools.get_match(data, '\?id=(\d+)" rel="nofollow"')

    start = data.find('<select id="sseriesSeason">')
    end = data.find('</select>', start)

    for season_id, season in re.compile('<option value="([^"]+)">([^<]+)</option>').findall(data[start:end]):
        post_data = 'news_id=%s&season=%s' % (serie_id, season_id)
        json = scrapertools.cache_page(post_url, post=post_data, headers=headers)
        for episode_id, episode in re.compile(r'<option value=\\"(\d+)\\">([^<]+)<\\/option>').findall(json):
            title = season + ' | ' + episode.replace('Serie', 'Episodio')
            url = '%s?news_id=%s&series=%s?%s' % (post_url, serie_id, episode_id, item.url)
            itemlist.append(
                    Item(channel=__channel__,
                         action="findvid_serie",
                         title=title.strip(),
                         url=url,
                         fulltitle=item.fulltitle,
                         show=item.show,
                         thumbnail=item.thumbnail))

    if config.get_library_support() and len(itemlist) != 0:
        itemlist.append(
                Item(channel=__channel__,
                     title=item.title,
                     url=item.url,
                     action="add_serie_to_library",
                     extra="episodios",
                     show=item.show))
        itemlist.append(
                Item(channel=__channel__,
                     title="Scarica tutti gli episodi della serie",
                     url=item.url,
                     action="download_all_episodes",
                     extra="episodios",
                     show=item.show))

    return itemlist


def findvid_serie(item):
    logger.info("streamondemand.filmstreampw findvideos")

    post_url, post_data, referer = item.url.split('?')

    headers.append(['Referer', referer])

    # Descarga la página
    data = scrapertools.cache_page(post_url, post=post_data, headers=headers)

    itemlist = servertools.find_video_items(data=data.replace(r'\/', '/'))

    for videoitem in itemlist:
        videoitem.title = videoitem.title
        videoitem.fulltitle = item.fulltitle
        videoitem.thumbnail = item.thumbnail
        videoitem.show = item.show
        videoitem.plot = item.plot
        videoitem.channel = __channel__

    return itemlist

def info(title):
    logger.info("streamondemand.filmstreampw info")
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

