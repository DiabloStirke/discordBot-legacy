from config import CONTROL_PANEL_URL, CONTROL_PANEL_TOKEN
import requests


class ControlPanelException(Exception):
    pass


class ControlPanelClient:
    def __init__(self, url=CONTROL_PANEL_URL, token=CONTROL_PANEL_TOKEN):
        self.url = url
        self.token = token

    def get_silksong_news(self):
        response = self._request('GET', '/api/silksong/news')
        if response.status_code >= 400:
            raise ControlPanelException(response.text, response.status_code)
        return response.json()

    def _request(self, method, endpoint, data=None, headers=None, **kwargs):
        return requests.request(
            method,
            f'{self.url}{endpoint}',
            json=data,
            headers=self._get_headers(headers),
            **kwargs
        )

    def _get_headers(self, headers):
        if headers is None:
            headers = {}
        headers['X-Auth-Token'] = self.token
        return headers
