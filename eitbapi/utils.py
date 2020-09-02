# -*- coding: utf8 -*-
from __future__ import unicode_literals
from bs4 import BeautifulSoup

import requests
import sys
import xml.etree.ElementTree as ET
import os
import json
import datetime
import pytz


if sys.version_info >= (3, 0, 0):
    # for Python 3
    PYTHON3 = True
else:
    PYTHON3 = False


EITB_PLAYLIST_BASE_URL = (
    "https://mam.eitb.eus/mam/REST/ServiceMultiweb/Playlist/MULTIWEBTV/{}"
)
EITB_VIDEO_BASE_URL = "https://www.eitb.tv/es/video/"
EITB_VIDEO_URL = "https://www.eitb.tv/es/video/{}/{}/{}/{}/"

EITB_BASE_URL = "https://www.eitb.tv/"

EITB_CACHED_PROGRAM_LIST_XML_URL = (
    "https://raw.githubusercontent.com/erral/eitbapi/master/cache.json"
)
EITB_TV_PROGRAM_LIST_XML_URL = "https://www.eitb.tv/eu/menu/getMenu/tv/"
EITB_RADIO_PROGRAM_LIST_XML_URL = "https://www.eitb.tv/es/menu/getMenu/radio/"

EITB_LAST_BROADCAST_URL = 'https://mam.eitb.eus/mam/REST/ServiceMultiweb/SmartPlaylistByDestination/MULTIWEBTV/12/BROADCST_DATE/DESC/{}/'

def safe_unicode(value, encoding="utf-8"):
    if PYTHON3:
        if isinstance(value, bytes):
            return value
        elif isinstance(value, str):
            try:
                value = bytes(value, encoding)
            except (UnicodeDecodeError):
                value = value.decode("utf-8", "replace")
        return value
    else:
        if isinstance(value, unicode):
            return value
        elif isinstance(value, basestring):
            try:
                value = unicode(value, encoding)
            except (UnicodeDecodeError):
                value = value.decode("utf-8", "replace")
        return value


def safe_encode(value, charset="utf-8"):
    if PYTHON3:
        return safe_unicode(value, charset).decode(charset)
    else:
        return safe_unicode(value, charset).encode(charset)


def xml_to_dict(data):
    try:
        root = ET.fromstring(data)
    except ET.ParseError:
        root = []
    d = {}
    for item in root:
        dd = {}
        for subitem in item:
            m = {}
            m["text"] = subitem.text
            m.update(subitem.attrib)
            dd[subitem.tag] = m

        d[dd["title"]["text"]] = dd

    return d


def build_program_list_by_hash(menu_hash, mode="tv", first=False):
    if mode == "tv":
        results = get_tv_submenu_data(menu_hash, first=first)
    elif mode == "radio":
        results = get_radio_submenu_data(menu_hash, first=first)
    return results


def get_tv_program_data():
    res = requests.get(EITB_CACHED_PROGRAM_LIST_XML_URL)
    try:
        result = res.json()
    except:
        result = []
    return result


def _get_tv_program_data():
    menudata = requests.get(EITB_TV_PROGRAM_LIST_XML_URL)
    menudict = xml_to_dict(menudata.content)
    menu_hash = (
        menudict.get("programas_az", {}).get("submenu", {}).get("hash", "")
    )  # noqa
    return build_program_list_by_hash(menu_hash, mode="tv", first=True)


def get_tv_program_data_per_type(menu_hash):
    return build_program_list_by_hash(menu_hash, mode="tv")


def get_tv_program_types():
    menudata = requests.get(EITB_TV_PROGRAM_LIST_XML_URL)
    menudict = xml_to_dict(menudata.content)
    menu_hash = (
        menudict.get("por_categorias", {}).get("submenu", {}).get("hash", "")
    )  # noqa
    categorydata = requests.get(EITB_TV_PROGRAM_LIST_XML_URL + "/" + menu_hash)
    categorydict = xml_to_dict(categorydata.content)
    return categorydict


def get_tv_news_programs():
    menudata = requests.get(EITB_TV_PROGRAM_LIST_XML_URL)
    menudict = xml_to_dict(menudata.content)
    menu_hash = (
        menudict.get("informativos", {}).get("submenu", {}).get("hash", "")
    )  # noqa
    categorydata = requests.get(EITB_TV_PROGRAM_LIST_XML_URL + "/" + menu_hash)
    categorydict = xml_to_dict(categorydata.content)
    return categorydict

def get_last_broadcast_data(number_of_items):
    listdata = requests.get(EITB_LAST_BROADCAST_URL.format(number_of_items))
    listjson = json.loads(listdata.content)
    return listjson

def get_radio_program_data():
    results = []
    menudata = requests.get(EITB_RADIO_PROGRAM_LIST_XML_URL)
    menudict = xml_to_dict(menudata.content)
    menu_hash = (
        menudict.get("programas_az", {}).get("submenu", {}).get("hash", None)
    )  # noqa
    results = get_radio_submenu_data(menu_hash, first=True)
    return results


def get_radio_program_types():
    menudata = requests.get(EITB_RADIO_PROGRAM_LIST_XML_URL)
    menudict = xml_to_dict(menudata.content)
    menu_hash = (
        menudict.get("por_categorias", {}).get("submenu", {}).get("hash", "")
    )  # noqa
    categorydata = requests.get(
        EITB_RADIO_PROGRAM_LIST_XML_URL + "/" + menu_hash
    )  # noqa
    categorydict = xml_to_dict(categorydata.content)
    return categorydict


def get_radio_stations():
    menudata = requests.get(EITB_RADIO_PROGRAM_LIST_XML_URL)
    menudict = xml_to_dict(menudata.content)
    menu_hash = (
        menudict.get("por_emisoras", {}).get("submenu", {}).get("hash", "")
    )  # noqa
    categorydata = requests.get(
        EITB_RADIO_PROGRAM_LIST_XML_URL + "/" + menu_hash
    )  # noqa
    categorydict = xml_to_dict(categorydata.content)
    return categorydict


def get_tv_submenu_data(menu_hash, pretitle="", first=False):
    submenudata = requests.get(EITB_TV_PROGRAM_LIST_XML_URL + "/" + menu_hash)
    submenudict = xml_to_dict(submenudata.content)
    results = []
    for item in submenudict.values():
        subhash = item.get("submenu", {}).get("hash", None)
        if subhash:
            if first:
                results += get_tv_submenu_data(subhash)
            else:
                results += get_tv_submenu_data(
                    subhash, pretitle=item.get("title").get("text")
                )  # noqa

        data = {}
        data["title"] = (
            pretitle + " " + item.get("title", {}).get("text", "")
        ).strip()  # noqa
        data["id"] = item.get("id", {}).get("text", "")
        if data["id"]:
            results.append(data)

    return results


def get_radio_submenu_data(menu_hash, pretitle="", first=False):
    submenudata = requests.get(
        EITB_RADIO_PROGRAM_LIST_XML_URL + "/" + menu_hash
    )  # noqa
    submenudict = xml_to_dict(submenudata.content)
    results = []
    for item in submenudict.values():
        subhash = item.get("submenu", {}).get("hash", None)
        if subhash:
            if first:
                results += get_radio_submenu_data(subhash)
            else:
                results += get_radio_submenu_data(
                    subhash, pretitle=item.get("title").get("text")
                )  # noqa

        data = {}
        data["title"] = (
            pretitle + " " + item.get("title", {}).get("text", "")
        ).strip()  # noqa
        data["id"] = item.get("id", {}).get("text", "")
        if data["id"]:
            results.append(data)

    return results


def create_internal_video_url(
    playlist_title, playlist_id, video_title, video_id, request=None
):  # noqa
    """create an internal url to identify an episode inside this API."""
    playlist_title = clean_title(playlist_title)
    video_title = clean_title(playlist_title)

    internal_url = "{}/{}/{}/{}".format(
        playlist_title, playlist_id, video_id, video_title
    )  # noqa
    return request.route_url("episode", episode_url=internal_url)


def clean_title(title):
    """slugify the titles using the method that EITB uses in
       the website:
       - url: http://www.eitb.tv/resources/js/comun/comun.js
       - method: string2url
    """
    translation_map = {
        "À": "A",
        "Á": "A",
        "Â": "A",
        "Ã": "A",
        "Ä": "A",
        "Å": "A",
        "Æ": "E",
        "È": "E",
        "É": "E",
        "Ê": "E",
        "Ë": "E",
        "Ì": "I",
        "Í": "I",
        "Î": "I",
        "Ï": "I",
        "Ò": "O",
        "Ó": "O",
        "Ô": "O",
        "Ö": "O",
        "Ù": "U",
        "Ú": "U",
        "Û": "U",
        "Ü": "U",
        "Ñ": "N",
        "?": "",
        "¿": "",
        "!": "",
        "¡": "",
        ":": "",
        "_": "-",
        "º": "",
        "ª": "a",
        ",": "",
        ".": "",
        "(": "",
        ")": "",
        "@": "",
        " ": "-",
        "&": "",
        "#": "",
    }

    val = title.upper()
    for k, v in translation_map.items():
        val = val.replace(k, v)
    return val.lower()


def get_radio_programs(playlist_id):
    while playlist_id.startswith("/"):
        playlist_id = playlist_id[1:]

    results = []
    data = requests.get(EITB_BASE_URL + playlist_id)
    soup = BeautifulSoup(data.text, "html.parser")
    for li in soup.find_all("li", class_="audio_uno"):
        title_p, date_p, download_p = li.find_all("p")
        title = title_p.find("a").get("original-title")
        date, duration = date_p.text.split()
        url = download_p.find("a").get("href")
        duration = duration.replace("(", "").replace(")", "")
        item = dict(title=title, date=date, url=url, duration=duration)
        results.append(item)
    return results


def get_radio_program_data_per_type(playlist_id):
    return build_program_list_by_hash(playlist_id, mode="radio", first=True)


def get_radio_program_data_per_station(station_id):
    return build_program_list_by_hash(station_id, mode='radio', first=False)

# PARSE DATE TO ISO FORMAT
def date_to_iso_format(date):
    dateformat = '%Y-%m-%d %H:%M:%S'
    tz = pytz.timezone('Europe/Madrid')
    try:
        date_to_format = datetime.datetime.strptime(date, dateformat)
        date_to_format = tz.localize(date_to_format)
        dateiso = date_to_format.isoformat()
    except (TypeError, ValueError):
        dateiso = date
    return dateiso