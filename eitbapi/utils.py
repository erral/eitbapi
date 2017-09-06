from __future__ import unicode_literals

import requests
import sys
import xml.etree.ElementTree as ET

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


def get_tv_program_data():
    results = []
    menudata = requests.get(EITB_TV_PROGRAM_LIST_XML_URL)
    menudict = xml_to_dict(menudata.content)
    menu_hash = menudict.get('programas_az', {}).get('submenu', {}).get('hash', '')

    submenudata = requests.get(EITB_TV_PROGRAM_LIST_XML_URL + '/' + menu_hash)
    submenudict = xml_to_dict(submenudata.content)

    for item in submenudict.values():
        subhash = item.get('submenu', {}).get('hash')
        subsubmenudata = requests.get(EITB_TV_PROGRAM_LIST_XML_URL + '/' + subhash)
        subsubmenudict = xml_to_dict(subsubmenudata.content)
        for program in subsubmenudict.values():
            data = {}
            data['title'] = program.get('title', {}).get('text', '')
            data['id'] = program.get('id', {}).get('text', '')
            if data['id']:
                results.append(data)

    return results


def get_radio_program_data():
    results = []
    menudata = requests.get(EITB_RADIO_PROGRAM_LIST_XML_URL)
    menudict = xml_to_dict(menudata.content)
    menu_hash = menudict.get('programas_az', {}).get('submenu', {}).get('hash', None)

    results = get_submenu_data(menu_hash, first=True)

    return results


def get_submenu_data(menu_hash, pretitle='', first=False):
    #import pdb; pdb.set_trace()
    submenudata = requests.get(EITB_RADIO_PROGRAM_LIST_XML_URL + '/' + menu_hash)
    submenudict = xml_to_dict(submenudata.content)
    results = []
    for item in submenudict.values():
        subhash = item.get('submenu', {}).get('hash', None)
        if subhash:
            if first:
                results += get_submenu_data(subhash)
            else:
                results += get_submenu_data(subhash, pretitle=item.get('title').get('text'))

        data = {}
        data['title'] = pretitle + ' ' + item.get('title', {}).get('text', '')
        data['id'] = item.get('id', {}).get('text', '')
        if data['id']:
            results.append(data)

    return results
