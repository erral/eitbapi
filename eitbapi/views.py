# -*- coding: utf8 -*-
from __future__ import unicode_literals
from bs4 import BeautifulSoup
from pyramid.view import view_config
from eitbapi.utils import EITB_EPISODE_LIST_REGEX
from eitbapi.utils import EITB_FRONT_PAGE_URL
from eitbapi.utils import EITB_PLAYLIST_BASE_URL
from eitbapi.utils import EITB_VIDEO_BASE_URL
from eitbapi.utils import EITB_VIDEO_URL
from eitbapi.utils import EITB_RADIO_ITEMS_URL
from eitbapi.utils import EITB_BASE_URL

import datetime
import json
import os
import pytz
import re
import redis
import requests
import youtube_dl


if os.environ.get('REDIS_URL'):
    r = redis.from_url(os.environ.get("REDIS_URL"))
else:
    r = {}


@view_config(route_name='home', renderer='templates/index.pt')
def index(request):
    return {'project': 'eitbapi'}


@view_config(route_name='programs', renderer='prettyjson')
def programs(request):
    """get all information about all the programs.
    How: scrap the website and look for the javascript links.
    """
    data = requests.get(EITB_FRONT_PAGE_URL)
    matches = re.compile(EITB_EPISODE_LIST_REGEX, re.DOTALL).findall(data.text)

    result = {
        '@context': 'http://www.w3.org/ns/hydra/context.jsonld',
        '@id': request.route_url('programs'),
        '@type': 'TV',
        'parent': {},
    }

    results = []

    for id, title1, title2 in matches:
        scrapedtitle = title1
        if title1 != title2:
            scrapedtitle = scrapedtitle + " - " + title2

        data = {
            '@id': request.route_url('playlist', playlist_id=id),
            '@type': 'Playlist',
            'title': scrapedtitle,
            'description': '',
        }
        if data not in results:
            results.append(data)

    result['member'] = sorted(results, key=lambda x: x.get('title', '').lower())

    return result


def extract_radio_info_from_url(url):
    """ /eu/irratia/gaztea/akabo-bakea/3601966/" """
    _, lang, _, radio, lowertitle, id, _ = url.split('/')
    return dict(
        id=url[1:],
        title=lowertitle.replace('-', ' ').capitalize(),
        radio=radio.replace('-', ' ').capitalize(),
    )


@view_config(route_name='radio', renderer='prettyjson')
def radio(request):
    """get all information about all the programs.
    How: scrap the website and look for the javascript links.
    """
    result = {
        '@context': 'http://www.w3.org/ns/hydra/context.jsonld',
        '@id': request.route_url('radio'),
        '@type': 'Radio',
        'parent': {},
    }

    results = []

    data = requests.get(EITB_RADIO_ITEMS_URL)
    soup = BeautifulSoup(data.text, "html.parser")
    results = []
    programsoup = soup.find_all('li', class_='submenu', rel='programas_az')[0]
    for li in programsoup.find_all('li', class_='sbmntmp'):
        name = li.find('span', class_='nomtmp')
        program_name = u''
        if name:
            program_name = name.text

        for link in li.find_all('a'):
            if link.get('href').startswith('/eu/irratia/') or link.get('href').startswith('/es/radio/'):
                info = extract_radio_info_from_url(link.get('href'))
                id = info.get('id')
                title = link.text
                radio = info.get('radio')
                results.append({
                    '@id': request.route_url('radioplaylist', playlist_id=id),
                    '@type': 'Radio Playlist',
                    'title': u'{} - {}'.format(program_name, title),
                    'description': '',
                    'radio': radio
                })

    result['member'] = sorted(results, key=lambda x: x.get('title', '').lower())

    return result


@view_config(route_name='playlist', renderer='prettyjson')
def playlist(request):
    """ get all the information about the given program.
        How: get the information from a pseudo-api
    """
    playlist_id = request.matchdict['playlist_id']

    try:
        result = r.get(playlist_id)
    except:
        result = None

    if result is not None:
        return json.loads(result)

    else:

        result = {
            '@context': 'http://www.w3.org/ns/hydra/context.jsonld',
            '@id': request.route_url('playlist', playlist_id=playlist_id),
            '@type': 'Playlist',
            'parent': request.route_url('programs'),
        }

        playlist_url = EITB_PLAYLIST_BASE_URL.format(playlist_id)
        data = requests.get(playlist_url)
        playlist_data = data.json()
        web_medias = playlist_data.get('web_media')
        del playlist_data['web_media']

        member = []
        for web_media in web_medias:
            language = web_media.get('IDIOMA', '')
            pubdatestr = web_media.get('PUB_DATE', '')
            broadcastdatestr = web_media.get('BROADCST_DATE', '')
            dateformat = '%Y-%m-%d %H:%M:%S'

            tz = pytz.timezone('Europe/Madrid')
            try:
                pubdate = datetime.datetime.strptime(pubdatestr, dateformat)
                pubdate = tz.localize(pubdate)
                pubdateiso = pubdate.isoformat()
            except:
                pubdateiso = pubdatestr

            try:
                broadcastdate = datetime.datetime.strptime(broadcastdatestr, dateformat)
                broadcastdate = tz.localize(broadcastdate)
                broadcastdateiso = broadcastdate.isoformat()
            except:
                broadcastdateiso = broadcastdatestr
            item = {
                '@id': create_internal_video_url(
                    playlist_data.get('name_playlist'),
                    playlist_data.get('id_web_playlist'),
                    web_media.get('NAME_ES'),
                    web_media.get('ID_WEB_MEDIA'),
                    request=request,
                ),
                '@type': 'Episode',
                'title': web_media.get('NAME_{}'.format(language)),
                'title_eu': web_media.get('NAME_EU'),
                'title_es': web_media.get('NAME_ES'),
                'description': web_media.get('SHORT_DESC_{}'.format(language)),
                'description_eu': web_media.get('SHORT_DESC_EU', ''),
                'description_es': web_media.get('SHORT_DESC_ES', ''),
                'publication_date': pubdateiso,
                'broadcast_date': broadcastdateiso,
                'episode_image': web_media.get('STILL_URL', ''),
                'episode_image_thumbnail': web_media.get('THUMBNAIL_URL', ''),
                'language': language.lower(),
            }
            if item not in member:
                member.append(item)
        playlist_data['member'] = sorted(member, key=lambda x: x.get('broadcast_date'), reverse=True)

        del playlist_data['id']

        result.update(playlist_data)
        try:
            r.set(playlist_id, json.dumps(result))
        except:
            pass
        return result


@view_config(route_name='radioplaylist', renderer='prettyjson')
def radioplaylist(request):
    """ get all the information about the given program.
    """
    playlist_id = request.matchdict['playlist_id']

    try:
        result = r.get(playlist_id)
    except:
        result = None

    if result is not None:
        return json.loads(result)

    else:
        result = {
            '@context': 'http://www.w3.org/ns/hydra/context.jsonld',
            '@id': request.route_url('radioplaylist', playlist_id=playlist_id),
            '@type': 'Radio Playlist',
            'parent': request.route_url('radio'),
        }
        results = []
        data = requests.get(EITB_BASE_URL + playlist_id)
        soup = BeautifulSoup(data.text, "html.parser")
        for li in soup.find_all('li', class_='audio_uno'):
            title_p, date_p, download_p = li.find_all('p')
            title = title_p.find('a').get('original-title')
            date, duration = date_p.text.split()
            url = download_p.find('a').get('href')
            duration = duration.replace('(', '').replace(')', '')
            item = {
                '@id': '',
                '@type': 'Radio Program',
                '@context': 'http://www.w3.org/ns/hydra/context.jsonld',
                'title': title,
                'date': date,
                'duration': duration,
                'url': url,
            }
            if item not in results:
                results.append(item)

        result['member'] = sorted(results, key=lambda x: x.get('date', ''), reverse=True)
        return result


@view_config(route_name='episode', renderer='prettyjson')
def episode(request):
    """ Get all the information and the video links from a given episode.
        How: use youtube-dl to get the information
    """
    episode_url = request.matchdict['episode_url']

    try:
        result = r.get(episode_url)
    except:
        result = None

    if result is not None:
        return json.loads(result)
    else:
        url = EITB_VIDEO_BASE_URL + episode_url

        playlist_title, playlist_id, video_title, video_id = episode_url.split('/')
        result = {
            '@context': 'http://www.w3.org/ns/hydra/context.jsonld',
            '@id': request.route_url('episode', episode_url=episode_url),
            '@type': 'Episode',
            'parent': request.route_url('playlist', playlist_id=playlist_id),
        }

        ydl = youtube_dl.YoutubeDL({'outtmpl': '%(id)s%(ext)s'})
        video_data = ydl.extract_info(url, download=False)

        result.update(video_data)

        try:
            r.set(episode_url, json.dumps(result))
        except:
            pass

        return result


def clean_title(title):
    """slugify the titles using the method that EITB uses in
       the website:
       - url: http://www.eitb.tv/resources/js/comun/comun.js
       - method: string2url
    """
    translation_map = {
        'À': 'A', 'Á': 'A', 'Â': 'A', 'Ã': 'A', 'Ä': 'A', 'Å': 'A', 'Æ': 'E',
        'È': 'E', 'É': 'E', 'Ê': 'E', 'Ë': 'E',
        'Ì': 'I', 'Í': 'I', 'Î': 'I', 'Ï': 'I',
        'Ò': 'O', 'Ó': 'O', 'Ô': 'O', 'Ö': 'O',
        'Ù': 'U', 'Ú': 'U', 'Û': 'U', 'Ü': 'U',
        'Ñ': 'N', '?': '', '¿': '', '!': '',
        '¡': '', ': ': '', '_': '-', 'º': '',
        'ª': 'a', ',': '', '.': '', '(': '',
        ')': '', '@': '', ' ': '-', '&': ''
    }

    val = title.upper()
    for k, v in translation_map.items():
        val = val.replace(k, v)
    return val.lower()


def create_internal_video_url(playlist_title, playlist_id, video_title, video_id, request=None):
    """create an internal url to identify an episode inside this API."""
    playlist_title = clean_title(playlist_title)
    video_title = clean_title(playlist_title)

    internal_url = '{}/{}/{}/{}'.format(playlist_title, playlist_id, video_id, video_title)
    return request.route_url('episode', episode_url=internal_url)


def create_video_url(playlist_title, playlist_id, video_title, video_id):
    """create the URL of a given episode to be used with youtube-dl."""
    playlist_title = clean_title(playlist_title)
    video_title = clean_title(playlist_title)

    return EITB_VIDEO_URL.format(playlist_title, playlist_id, video_id, video_title)


def get_video_urls(playlist_title, playlist_id, video_title, video_id):
    """helper method to get the information from youtube-dl"""
    ydl = youtube_dl.YoutubeDL({'outtmpl': '%(id)s%(ext)s'})
    url = create_video_url(playlist_title, playlist_id, video_title, video_id)
    result = ydl.extract_info(url, download=False)
    return result
