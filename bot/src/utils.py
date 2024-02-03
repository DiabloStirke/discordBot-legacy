from zoneinfo import ZoneInfo
from datetime import datetime
import requests
from lxml import etree
from io import StringIO
import re
import time
from urllib.parse import urlparse, parse_qs
from typing import Tuple, Callable, Coroutine
import functools
import asyncio
from config import TZ


def get_webpage(url):
    response = requests.get(url)
    dom_tree = etree.parse(
        StringIO(response.content.decode('utf-8')),
        parser=etree.HTMLParser()
    )

    return dom_tree


def find_vc(guild, name):
    for _vc in guild.voice_channels:
        if name == _vc.name:
            return _vc
    return None


def valid_url(url):
    regex = re.compile(
        r'^(?:http)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # noqa: E501 /// domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(regex, url) is not None


def valid_youtube_url(url: str) -> Tuple[bool, bool]:
    """Check wether the url is a valid youtube video or playlist

    Returns a tuple of 2 booleans: (is_a_valid_video, is_a_valid_playlist)
    """
    regex = re.compile(
        r'^(https?://)?(www\.)?youtu((.be)|(be\.com))(/[A-Z?=&\d\-_]+)+/?$', re.IGNORECASE
    )
    if re.match(regex, url) is None:
        return False, False

    parsed_url = urlparse(url)
    query = parse_qs(parsed_url.query)

    is_a_valid_video = 'v' in query and parsed_url.path == '/watch'
    is_a_valid_playlist = 'list' in query and parsed_url.path in ['/watch', '/playlist']

    return is_a_valid_video, is_a_valid_playlist


def verbose_time_from_seconds(seconds):
    t = time.gmtime(seconds)
    thstr = "" if t.tm_hour == 0 else f'{t.tm_hour} {"hours" if t.tm_hour != 1 else "hour"} '
    tmstr = "" if t.tm_min == 0 and not thstr else f'{t.tm_min} {"minutes" if t.tm_min != 1 else "minute"} '  # noqa: E501
    tsstr = f'{t.tm_sec} {"seconds" if t.tm_sec != 1 else "second"}'

    return thstr + tmstr + tsstr


def ordinal(n: int):
    if 11 <= (n % 100) <= 13:
        suffix = 'th'
    else:
        suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
    return str(n) + suffix


def to_thread(func: Callable) -> Coroutine:
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        return await asyncio.to_thread(func, *args, **kwargs)
    return wrapper


def tz_now(tz=TZ):
    tz = ZoneInfo(tz)
    return datetime.now(tz=tz)


def tz_fromiso(iso_date, tz=TZ):
    tz = ZoneInfo(tz)
    return datetime.fromisoformat(iso_date).astimezone(tz)
