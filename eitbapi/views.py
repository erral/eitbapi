from __future__ import unicode_literals
from pyramid.view import view_config
from utils import EITB_FRONT_PAGE_URL
from utils import EITB_EPISODE_LIST_REGEX
from utils import EITB_PLAYLIST_BASE_URL
from utils import EITB_VIDEO_URL
from utils import EITB_VIDEO_BASE_URL


import requests
import re
import youtube_dl


@view_config(route_name='home', renderer='templates/index.pt')
def index(request):
    return {'project': 'eitbapi'}


@view_config(route_name='programs', renderer='prettyjson')
def programs(request):
    data = requests.get(EITB_FRONT_PAGE_URL)
    matches = re.compile(EITB_EPISODE_LIST_REGEX, re.DOTALL).findall(data.text)

    result = {
        '@context': 'http://www.w3.org/ns/hydra/context.jsonld',
        '@id': request.route_url('home'),
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
    playlist_id = request.matchdict['playlist_id']
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
            '@id': create_video_url(
                playlist_data.get('name_playlist'),
                playlist_data.get('id_web_playlist'),
                web_media.get('NAME_ES'),
                web_media.get('ID_WEB_MEDIA'),
                add_domain=False,
                request=request,
            ),
            'title': web_media.get('NAME_ES'),
            'description': '',
        }
        playlist_data['member'].append(item)
    del playlist_data['id']

    result.update(playlist_data)

    return result


@view_config(route_name='episode', renderer='prettyjson')
def episode(request):
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


def create_video_url(playlist_title, playlist_id, video_title, video_id, add_domain=True, request=None):
    playlist_title = playlist_title.lower().replace(' ', '-').replace('(', '').replace(')', '')
    video_title = playlist_title.lower().replace(' ', '-').replace('(', '').replace(')', '')

    if add_domain:
        url = EITB_VIDEO_URL.format(playlist_title, playlist_id, video_id, video_title)
    else:
        internal_url = '{}/{}/{}/{}'.format(playlist_title, playlist_id, video_id, video_title)
        url = request.route_url('episode', episode_url=internal_url)
    return url


def get_video_urls(playlist_title, playlist_id, video_title, video_id):
    ydl = youtube_dl.YoutubeDL({'outtmpl': '%(id)s%(ext)s'})
    url = create_video_url(playlist_title, playlist_id, video_title, video_id)
    import pdb; pdb.set_trace()

    result = ydl.extract_info(url, download=False)

    return result
