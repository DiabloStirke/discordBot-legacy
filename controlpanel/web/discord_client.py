import requests
from urllib.parse import quote


class DiscordClientException(Exception):
    pass


class DiscordClient:
    BASE_URL = 'https://discord.com/api/v10'

    def __init__(self, client_id=None, client_secret=None, bot_token=None):
        self.client_id = None
        self.client_secret = None
        self.bot_token = None

        if bot_token:
            self.bot_token = bot_token
        elif client_id and client_secret:
            self.client_id = client_id
            self.client_secret = client_secret
        else:
            raise ValueError('You must provide either a bot token or a client id and secret')

    def get_authorization_url(self, redirect_uri, scopes=None):
        if scopes is None:
            scopes = self.get_scopes()
        redirect_uri = quote(redirect_uri, safe='')
        return (
            f"{self.BASE_URL}/oauth2/authorize?client_id={self.client_id}"
            + f"&redirect_uri={redirect_uri}&response_type=code&scope={scopes}"
        )

    def exchange_code(self, code, redirect_uri):
        url = f"{self.BASE_URL}/oauth2/token"
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': redirect_uri
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        response = requests.post(url, data=data, headers=headers, auth=(
            self.client_id, self.client_secret
        ))
        if response.status_code != 200:
            raise DiscordClientException(response.content, response.status_code)
        return response.json()

    def revoke_token(self, token):
        url = f"{self.BASE_URL}/oauth2/token/revoke"
        data = {
            'token': token,
            'token_type_hint': 'access_token'
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        response = requests.post(url, data=data, headers=headers, auth=(
            self.client_id, self.client_secret
        ))
        if response.status_code != 200:
            raise DiscordClientException(response.content, response.status_code)
        return response.json()

    def refresh_token(self, refresh_token):
        url = f"{self.BASE_URL}/oauth2/token"
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        response = requests.post(url, data=data, headers=headers, auth=(
            self.client_id, self.client_secret
        ))
        if response.status_code != 200:
            raise DiscordClientException(response.content, response.status_code)
        return response.json()

    def me(self, token=None):
        url = f"{self.BASE_URL}/users/@me"
        return self._request('GET', url, token)

    def get_avatar_url(self, token=None):
        user = self.me(token)
        return f"https://cdn.discordapp.com/avatars/{user['id']}/{user['avatar']}.png"

    def send_message(self, channel_id, content, token=None):
        url = f"{self.BASE_URL}/channels/{channel_id}/messages"
        data = {
            'content': content
        }
        return self._request('POST', url, token, data)

    def get_dm_channel(self, user_id, token=None):
        url = f"{self.BASE_URL}/users/@me/channels"
        data = {
            'recipient_id': user_id
        }
        return self._request('POST', url, token, data)

    def send_dm(self, user_id, content, token=None):
        channel = self.get_dm_channel(user_id, token)
        return self.send_message(channel['id'], content, token)

    def _request(self, method, url, token=None, data=None):
        if not token and not self.bot_token:
            raise ValueError('You must provide a token or a bot token to make requests')
        headers = {
            'Authorization': f'Bearer {token}' if token else f'Bot {self.bot_token}'
        }
        response = requests.request(method, url, headers=headers, json=data)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            raise DiscordClientException(response.content, response.status_code)
        return response.json()

    @staticmethod
    def get_scopes(
        activities_read=False,
        activities_write=False,
        applications_builds_read=False,
        applications_builds_upload=False,
        applications_commands=False,
        applications_commands_update=False,
        applications_commands_permissions_update=False,
        applications_entitlements=False,
        applications_store_update=False,
        bot=False,
        connections=False,
        dm_channels_read=False,
        email=False,
        gdm_join=False,
        guilds=False,
        guilds_join=False,
        guilds_members_read=False,
        identify=True,
        messages_read=False,
        relationships_read=False,
        role_connections_write=False,
        rpc=False,
        rpc_activities_write=False,
        rpc_notifications_read=False,
        rpc_voice_read=False,
        rpc_voice_write=False,
        voice=False,
        webhook_incoming=False,
    ):
        scopes = [key.replace('_', '.') for key, value in locals().items() if value]
        return '%20'.join(scopes)
