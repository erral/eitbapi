# -*- coding: utf8 -*-
from __future__ import unicode_literals
from eitbapi.utils import create_internal_video_url
from eitbapi.utils import EITB_PLAYLIST_BASE_URL
from eitbapi.utils import EITB_VIDEO_BASE_URL
from eitbapi.utils import get_tv_news_programs
from eitbapi.utils import get_tv_program_data
from eitbapi.utils import get_tv_program_data_per_type
from eitbapi.utils import get_tv_program_types
from eitbapi.utils import safe_encode
from pyramid.view import view_config

import datetime
import pytz
import requests
import youtube_dl


def prepare_program_list(request, menudata):
    result = {
        '@context': 'http://www.w3.org/ns/hydra/context.jsonld',
        '@id': request.route_url('programs'),
        '@type': 'TV',
        'parent': {},
    }

    results = []

    for item in menudata:
        data = {
            '@id': request.route_url('playlist', playlist_id=item.get('id')),
            '@type': 'Playlist',
            'title': safe_encode(item.get('title')),
            'description': '',
        }
        if data not in results:
            results.append(data)

    result['member'] = sorted(results, key=lambda x: x.get('title', u'').lower())

    return result


@view_config(route_name='programs', renderer='prettyjson')
def programs(request):
    """get all information about all the programs.
    How: scrap the website and look for the javascript links.
    """
    menudata = get_tv_program_data()
    return prepare_program_list(request, menudata)


@view_config(route_name='program-type-list', renderer='prettyjson')
def program_type_list(request):
    result = {
        '@context': 'http://www.w3.org/ns/hydra/context.jsonld',
        '@id': request.route_url('program-type-list'),
        '@type': 'TypeList',
        'parent': request.route_url('home'),
        'member': []
    }
    member = []
    categorydict = get_tv_program_types(request)
    for categoryname, categoryvalues in categorydict.items():
        item = {
            '@id': request.route_url('playlist-per-type', playlist_id=categoryvalues.get('submenu', {}).get('hash', '')),
            '@type': 'Type-Playlist',
            'parent': request.route_url('program-type-list'),
            'title': categoryname
        }
        member.append(item)

    result['member'] = sorted(member, key=lambda x: x.get('title'))
    return result


@view_config(route_name='program-type-news', renderer='prettyjson')
def program_type_news(request):
    result = {
        '@context': 'http://www.w3.org/ns/hydra/context.jsonld',
        '@id': request.route_url('program-type-list'),
        '@type': 'TypeList',
        'parent': request.route_url('home'),
        'member': []
    }
    member = []
    categorydict = get_tv_news_programs(request)
    for categoryname, categoryvalues in categorydict.items():
        item = {
            '@id': request.route_url('playlist-per-type', playlist_id=categoryvalues.get('submenu', {}).get('hash', '')),
            '@type': 'Type-Playlist',
            'parent': request.route_url('program-type-list'),
            'title': categoryname
        }
        member.append(item)

    result['member'] = sorted(member, key=lambda x: x.get('title'))
    return result


@view_config(route_name='playlist-per-type', renderer='prettyjson')
def programs_per_type(request):
    playlist_id = request.matchdict['playlist_id']
    menudata = get_tv_program_data_per_type(playlist_id)
    return prepare_program_list(request, menudata)


@view_config(route_name='playlist', renderer='prettyjson')
def playlist(request):
    """ get all the information about the given program.
        How: get the information from a pseudo-api
    """
    playlist_id = request.matchdict['playlist_id']

    result = {
        '@context': 'http://www.w3.org/ns/hydra/context.jsonld',
        '@id': request.route_url('playlist', playlist_id=playlist_id),
        '@type': 'Playlist',
        'parent': request.route_url('programs'),
    }

    playlist_url = EITB_PLAYLIST_BASE_URL.format(playlist_id)
    try:
        data = requests.get(playlist_url)
        playlist_data = data.json()
    except ValueError:
        return result

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
    return result


@view_config(route_name='episode', renderer='prettyjson')
def episode(request):
    """ Get all the information and the video links from a given episode.
        How: use youtube-dl to get the information
    """
    episode_url = request.matchdict['episode_url']

    url = EITB_VIDEO_BASE_URL + episode_url
    try:
        playlist_title, playlist_id, video_title, video_id = episode_url.split('/')
    except ValueError:
        return {}

    result = {
        '@context': 'http://www.w3.org/ns/hydra/context.jsonld',
        '@id': request.route_url('episode', episode_url=episode_url),
        '@type': 'Episode',
        'parent': request.route_url('playlist', playlist_id=playlist_id),
    }

    try:
        ydl = youtube_dl.YoutubeDL({'outtmpl': '%(id)s%(ext)s'})
        video_data = ydl.extract_info(url, download=False)
    except youtube_dl.DownloadError:
        return result

    result.update(video_data)
    return result
