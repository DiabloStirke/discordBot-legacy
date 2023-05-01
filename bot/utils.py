import requests
from lxml import etree
from io import StringIO
import re
import time

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
        r'^(?:http)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(regex, url) is not None

def verbouse_time_from_seconds(seconds):
    t = time.gmtime(seconds)
    thstr = "" if t.tm_hour == 0 else f'{t.tm_hour} {"hours" if t.tm_hour != 1 else "hour"} '
    tmstr = "" if t.tm_min == 0 and not thstr else f'{t.tm_min} {"minutes" if t.tm_min != 1 else "minute"} '
    tsstr = f'{t.tm_sec} {"seconds" if t.tm_sec != 1 else "second"}'
    
    return thstr + tmstr + tsstr
    
def ordinal(n: int):
    if 11 <= (n % 100) <= 13:
        suffix = 'th'
    else:
        suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
    return str(n) + suffix
