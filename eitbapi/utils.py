EITB_FRONT_PAGE_URL = "http://www.eitb.tv/eu/"
EITB_EPISODE_LIST_REGEX = "<li[^>]*>[^<]*<a href=\"\" onclick\=\"setPylstId\('(\d+)','([^']+)','([^']+)'\)\;"
EITB_PLAYLIST_BASE_URL = "http://www.eitb.tv/es/get/playlist/{}"
EITB_VIDEO_BASE_URL = "http://www.eitb.tv/es/video/"
EITB_VIDEO_URL = "http://www.eitb.tv/es/video/{}/{}/{}/{}/"

EITB_RADIO_ITEMS_URL = "http://www.eitb.tv/es/radio/"
EITB_BASE_URL = "http://www.eitb.tv/"

EITB_PROGRAM_LIST_HTML_URL_0 = 'http://www.eitb.tv/eu/menu/getMenu/tv/0/'
EITB_PROGRAM_LIST_HTML_URL_1 = 'http://www.eitb.tv/eu/menu/getMenu/tv/1/'
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
