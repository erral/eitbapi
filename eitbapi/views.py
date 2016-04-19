# -*- coding: utf8 -*-
from __future__ import unicode_literals
from pyramid.view import view_config
from utils import EITB_EPISODE_LIST_REGEX
from utils import EITB_FRONT_PAGE_URL
from utils import EITB_PLAYLIST_BASE_URL
from utils import EITB_VIDEO_BASE_URL
from utils import EITB_VIDEO_URL

import json
import os
import re
import redis
import requests
import youtube_dl

r = redis.from_url(os.environ.get("REDIS_URL"))


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
        '@type': 'SiteRoot',
        'parent': {},
    }

    results = []

    for id, title1, title2 in matches:
        scrapedtitle = title1
        if title1 != title2:
            scrapedtitle = scrapedtitle + " - " + title2

        results.append({
            '@id': request.route_url('playlist', playlist_id=id),
            'title': scrapedtitle,
            'description': '',
        })

    result['member'] = results

    return result


@view_config(route_name='playlist', renderer='prettyjson')
def playlist(request):
    """ get all the information about the given program.
        How: get the information from a pseudo-api
    """
    playlist_id = request.matchdict['playlist_id']

    result = r.get(playlist_id)
    print result
    if result is not None:
        print 'From redis'
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

        playlist_data['member'] = []
        for web_media in web_medias:
            item = {
                '@id': create_internal_video_url(
                    playlist_data.get('name_playlist'),
                    playlist_data.get('id_web_playlist'),
                    web_media.get('NAME_ES'),
                    web_media.get('ID_WEB_MEDIA'),
                    request=request,
                ),
                'title': web_media.get('NAME_ES'),
                'description': '',
            }
            playlist_data['member'].append(item)
        del playlist_data['id']

        result.update(playlist_data)

        r.set(playlist_id, json.dumps(result))
        print 'Not from redis'
        return result


@view_config(route_name='episode', renderer='prettyjson')
def episode(request):
    """ Get all the information and the video links from a given episode.
        How: use youtube-dl to get the information
    """
    episode_url = request.matchdict['episode_url']
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
