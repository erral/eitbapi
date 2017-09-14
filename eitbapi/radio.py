# -*- coding: utf8 -*-
from __future__ import unicode_literals
from eitbapi.utils import get_radio_program_data
from eitbapi.utils import get_radio_program_types
from eitbapi.utils import get_radio_programs
from eitbapi.utils import get_radio_program_data_per_type
from eitbapi.utils import safe_encode
from pyramid.view import view_config


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


@view_config(route_name='radio-program-type-list', renderer='prettyjson')
def radio_program_type_list(request):
    result = {
        '@context': 'http://www.w3.org/ns/hydra/context.jsonld',
        '@id': request.route_url('radio-program-type-list'),
        '@type': 'RadioTypeList',
        'parent': request.route_url('home'),
        'member': []
    }
    member = []
    categorydict = get_radio_program_types()
    for categoryname, categoryvalues in categorydict.items():
        item = {
            '@id': request.route_url(
                'radio-playlist-per-type',
                playlist_id=categoryvalues.get('submenu', {}).get('hash', '')
            ),
            '@type': 'Radio-Type-Playlist',
            'parent': request.route_url('radio-program-type-list'),
            'title': categoryname
        }
        member.append(item)

    result['member'] = sorted(member, key=lambda x: x.get('title', ''))
    return result


@view_config(route_name='radioplaylist', renderer='prettyjson')
def radioplaylist(request):
    """ get all the information about the given program.
    """
    playlist_id = request.matchdict['playlist_id']

    result = {
        '@context': 'http://www.w3.org/ns/hydra/context.jsonld',
        '@id': request.route_url('radioplaylist', playlist_id=playlist_id),
        '@type': 'Radio Playlist',
        'parent': request.route_url('radio'),
    }
    results = []
    radio_programs = get_radio_programs(playlist_id)
    for radio_program in radio_programs:
        item = {
            '@id': '',
            '@type': 'Radio Program',
            '@context': 'http://www.w3.org/ns/hydra/context.jsonld',
            'title': radio_program.get('title', ''),
            'date': radio_program.get('date', ''),
            'duration': radio_program.get('duration', ''),
            'url': radio_program.get('url', ''),
        }
        results.append(item)

    result['member'] = sorted(results, key=lambda x: x.get('date', ''), reverse=True)
    return result


@view_config(route_name='radio-playlist-per-type', renderer='prettyjson')
def radio_programs_per_type(request):
    playlist_id = request.matchdict['playlist_id']
    result = {
        '@context': 'http://www.w3.org/ns/hydra/context.jsonld',
        '@id': request.route_url('radioplaylist', playlist_id=playlist_id),
        '@type': 'Radio Program Type List',
        'parent': {},
    }
    menudata = get_radio_program_data_per_type(playlist_id)
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

    result['member'] = sorted(results, key=lambda x: x.get('title', ''))
    return result
