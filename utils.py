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