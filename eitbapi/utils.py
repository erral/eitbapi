import requests
import xml.etree.ElementTree as ET

EITB_FRONT_PAGE_URL = "http://www.eitb.tv/eu/"
EITB_EPISODE_LIST_REGEX = "<li[^>]*>[^<]*<a href=\"\" onclick\=\"setPylstId\('(\d+)','([^']+)','([^']+)'\)\;"
EITB_PLAYLIST_BASE_URL = "http://www.eitb.tv/es/get/playlist/{}"
EITB_VIDEO_BASE_URL = "http://www.eitb.tv/es/video/"
EITB_VIDEO_URL = "http://www.eitb.tv/es/video/{}/{}/{}/{}/"

EITB_RADIO_ITEMS_URL = "http://www.eitb.tv/es/radio/"
EITB_BASE_URL = "http://www.eitb.tv/"

EITB_PROGRAM_LIST_XML_URL = 'http://www.eitb.tv/eu/menu/getMenu/tv/'


EITB_RADIO_PROGRAM_LIST_HTML_URL_1 = 'http://www.eitb.tv/eu/menu/getMenu/radio/0/'


def safe_unicode(text, charset='utf-8'):
    if isinstance(text, unicode):
        return text
    if isinstance(text, str):
        return unicode(text, charset)
    else:
        try:
            return unicode(text)
        except:
            return ''


def xml_to_dict(data):
    root = ET.fromstring(data)
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

def get_program_data():
    results = []
    menudata = requests.get(EITB_PROGRAM_LIST_XML_URL)
    menudict = xml_to_dict(menudata.content)
    menu_hash = menudict.get('programas_az', {}).get('submenu', {}).get('hash', '')

    submenudata = requests.get(EITB_PROGRAM_LIST_XML_URL + '/' + menu_hash)
    submenudict = xml_to_dict(submenudata.content)

    for item in submenudict.values():
        subhash = item.get('submenu', {}).get('hash')
        subsubmenudata = requests.get(EITB_PROGRAM_LIST_XML_URL + '/' + subhash)
        subsubmenudict = xml_to_dict(subsubmenudata.content)
        for program in subsubmenudict.values():
            data = {}
            data['title'] = program.get('title', {}).get('text', '')
            data['id'] = program.get('id', {}).get('text', '')
            if data['id']:
                results.append(data)

    return results
