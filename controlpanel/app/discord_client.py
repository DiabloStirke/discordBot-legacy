import requests
from urllib.parse import quote


class DiscordClientException(Exception):
    pass


class DiscordClient:
    BASE_URL = 'https://discord.com/api/v10'

    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret

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

    def me(self, token):
        url = f"{self.BASE_URL}/users/@me"
        headers = {
            'Authorization': f'Bearer {token}'
        }
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            raise DiscordClientException(response.content, response.status_code)
        return response.json()

    def get_avatar_url(self, token):
        user = self.me(token)
        return f"https://cdn.discordapp.com/avatars/{user['id']}/{user['avatar']}.png"

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

