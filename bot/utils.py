import requests
from lxml import etree
from io import StringIO


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
