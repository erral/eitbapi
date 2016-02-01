from __future__ import unicode_literals
from pyramid.view import view_config
from utils import EITB_FRONT_PAGE_URL
from utils import EITB_EPISODE_LIST_REGEX
from utils import EITB_PLAYLIST_BASE_URL
from utils import EITB_VIDEO_URL

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

    results = []

    for id, title1, title2 in matches:
        scrapedtitle = title1
        if title1 != title2:
            scrapedtitle = scrapedtitle + " - " + title2

        results.append(dict(
            title=scrapedtitle,
            id=id,
        ))

    return results


@view_config(route_name='playlist', renderer='prettyjson')
def playlist(request):
    playlist_id = request.matchdict['playlist_id']
    playlist_url = EITB_PLAYLIST_BASE_URL.format(playlist_id)
    data = requests.get(playlist_url)
    playlist_data = data.json()
    web_medias = playlist_data.get('web_media')
    playlist_data['web_media'] = []
    new_web_medias = []

    for web_media in web_medias:

        web_media['videos'] = get_video_urls(
            playlist_data.get('name_playlist'),
            playlist_data.get('id_web_playlist'),
            web_media.get('NAME_ES'),
            web_media.get('ID_WEB_MEDIA'),
        )
        new_web_medias.append(web_media)


    playlist_data['web_media'] = new_web_medias
    return playlist_data


def get_video_urls(playlist_title, playlist_id, video_title, video_id):

    ydl = youtube_dl.YoutubeDL({'outtmpl': '%(id)s%(ext)s'})

    playlist_title = playlist_title.lower().replace(' ', '-').replace('(', '').replace(')', '')
    video_title = playlist_title.lower().replace(' ', '-').replace('(', '').replace(')', '')

    url = EITB_VIDEO_URL.format(playlist_title, playlist_id, video_id, video_title)
    result = ydl.extract_info(url, download=False)

    return result
