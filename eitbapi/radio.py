# -*- coding: utf8 -*-
from __future__ import unicode_literals
from bs4 import BeautifulSoup
from eitbapi.utils import EITB_BASE_URL
from eitbapi.utils import get_radio_program_data
from eitbapi.utils import safe_encode
from pyramid.view import view_config

import json
import os
import redis
import requests


if os.environ.get('REDIS_URL'):
    r = redis.from_url(os.environ.get("REDIS_URL"))
else:
    r = {}


@view_config(route_name='radio', renderer='prettyjson')
def radio(request):
    """get all information about all the programs.
    How: scrap the website and look for the javascript links.
    """
    menudata = get_radio_program_data()

    result = {
        '@context': 'http://www.w3.org/ns/hydra/context.jsonld',
        '@id': request.route_url('programs'),
        '@type': 'Radio',
        'parent': {},
    }

    results = []

    for item in menudata:
        data = {
            '@id': request.route_url('radioplaylist', playlist_id=item.get('id')),
            '@type': 'Radio Playlist',
            'title': safe_encode(item.get('title')),
            'description': '',
        }
        if data not in results:
            results.append(data)

    result['member'] = sorted(results, key=lambda x: x.get('title', u'').lower())

    return result


@view_config(route_name='radioplaylist', renderer='prettyjson')
def radioplaylist(request):
    """ get all the information about the given program.
    """
    playlist_id = request.matchdict['playlist_id']

    # try:
    #     result = r.get(playlist_id)
    # except:
    #     result = None
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
