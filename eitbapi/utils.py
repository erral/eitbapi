# -*- coding: utf8 -*-
from __future__ import unicode_literals

import requests
import sys
import xml.etree.ElementTree as ET
import youtube_dl

if sys.version_info >= (3, 0, 0):
    # for Python 3
    PYTHON3 = True
else:
    PYTHON3 = False


EITB_FRONT_PAGE_URL = "http://www.eitb.tv/eu/"
EITB_EPISODE_LIST_REGEX = r"<li[^>]*>[^<]*<a href=\"\" onclick\=\"setPylstId\('(\d+)','([^']+)','([^']+)'\)\;" # noqa
EITB_PLAYLIST_BASE_URL = "http://www.eitb.tv/es/get/playlist/{}"
EITB_VIDEO_BASE_URL = "http://www.eitb.tv/es/video/"
EITB_VIDEO_URL = "http://www.eitb.tv/es/video/{}/{}/{}/{}/"

EITB_RADIO_ITEMS_URL = "http://www.eitb.tv/es/radio/"
EITB_BASE_URL = "http://www.eitb.tv/"

EITB_TV_PROGRAM_LIST_XML_URL = 'http://www.eitb.tv/eu/menu/getMenu/tv/'
EITB_RADIO_PROGRAM_LIST_XML_URL = 'http://www.eitb.tv/es/menu/getMenu/radio/'


def safe_unicode(value, encoding='utf-8'):
    if PYTHON3:
        if isinstance(value, bytes):
            return value
        elif isinstance(value, str):
            try:
                value = bytes(value, encoding)
            except (UnicodeDecodeError):
                value = value.decode('utf-8', 'replace')
        return value
    else:
        if isinstance(value, unicode):
            return value
        elif isinstance(value, basestring):
            try:
                value = unicode(value, encoding)
            except (UnicodeDecodeError):
                value = value.decode('utf-8', 'replace')
        return value


def safe_encode(value, charset='utf-8'):
    if PYTHON3:
        return safe_unicode(value, charset).decode(charset)
    else:
        return safe_unicode(value, charset).encode(charset)


def xml_to_dict(data):
    try:
        root = ET.fromstring(data)
    except:
        root = []
    d = {}
    for item in root:
        dd = {}
        for subitem in item:
            m = {}
            m['text'] = subitem.text
            m.update(subitem.attrib)
            dd[subitem.tag] = m

        d[dd['title']['text']] = dd

    return d


def build_program_list_by_hash(menu_hash):
    results = get_tv_submenu_data(menu_hash, first=True)
    return results


def get_tv_program_data():
    menudata = requests.get(EITB_TV_PROGRAM_LIST_XML_URL)
    menudict = xml_to_dict(menudata.content)
    menu_hash = menudict.get('programas_az', {}).get('submenu', {}).get('hash', '')
    return build_program_list_by_hash(menu_hash)


def get_tv_program_data_per_type(menu_hash):
    return build_program_list_by_hash(menu_hash)


def get_tv_program_types(request):
    menudata = requests.get(EITB_TV_PROGRAM_LIST_XML_URL)
    menudict = xml_to_dict(menudata.content)
    menu_hash = menudict.get('por_categorias', {}).get('submenu', {}).get('hash', '')
    categorydata = requests.get(EITB_TV_PROGRAM_LIST_XML_URL + '/' + menu_hash)
    categorydict = xml_to_dict(categorydata.content)
    return categorydict


def get_tv_news_programs(request):
    menudata = requests.get(EITB_TV_PROGRAM_LIST_XML_URL)
    menudict = xml_to_dict(menudata.content)
    menu_hash = menudict.get('informativos', {}).get('submenu', {}).get('hash', '')
    categorydata = requests.get(EITB_TV_PROGRAM_LIST_XML_URL + '/' + menu_hash)
    categorydict = xml_to_dict(categorydata.content)
    return categorydict


def get_radio_program_data():
    results = []
    menudata = requests.get(EITB_RADIO_PROGRAM_LIST_XML_URL)
    menudict = xml_to_dict(menudata.content)
    menu_hash = menudict.get('programas_az', {}).get('submenu', {}).get('hash', None)

    results = get_radio_submenu_data(menu_hash, first=True)

    return results


def get_tv_submenu_data(menu_hash, pretitle='', first=False):
    submenudata = requests.get(EITB_TV_PROGRAM_LIST_XML_URL + '/' + menu_hash)
    submenudict = xml_to_dict(submenudata.content)
    results = []
    for item in submenudict.values():
        subhash = item.get('submenu', {}).get('hash', None)
        if subhash:
            if first:
                results += get_tv_submenu_data(subhash)
            else:
                results += get_tv_submenu_data(subhash, pretitle=item.get('title').get('text'))

        data = {}
        data['title'] = (pretitle + ' ' + item.get('title', {}).get('text', '')).strip()
        data['id'] = item.get('id', {}).get('text', '')
        if data['id']:
            results.append(data)

    return results


def get_radio_submenu_data(menu_hash, pretitle='', first=False):
    submenudata = requests.get(EITB_RADIO_PROGRAM_LIST_XML_URL + '/' + menu_hash)
    submenudict = xml_to_dict(submenudata.content)
    results = []
    for item in submenudict.values():
        subhash = item.get('submenu', {}).get('hash', None)
        if subhash:
            if first:
                results += get_radio_submenu_data(subhash)
            else:
                results += get_radio_submenu_data(subhash, pretitle=item.get('title').get('text'))

        data = {}
        data['title'] = (pretitle + ' ' + item.get('title', {}).get('text', '')).strip()
        data['id'] = item.get('id', {}).get('text', '')
        if data['id']:
            results.append(data)

    return results


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
        '¡': '', ':': '', '_': '-', 'º': '',
        'ª': 'a', ',': '', '.': '', '(': '',
        ')': '', '@': '', ' ': '-', '&': ''
    }

    val = title.upper()
    for k, v in translation_map.items():
        val = val.replace(k, v)
    return val.lower()


def extract_radio_info_from_url(url):
    """ /eu/irratia/gaztea/akabo-bakea/3601966/" """
    _, lang, _, radio, lowertitle, id, _ = url.split('/')
    return dict(
        id=url[1:],
        title=lowertitle.replace('-', ' ').capitalize(),
        radio=radio.replace('-', ' ').capitalize(),
    )
