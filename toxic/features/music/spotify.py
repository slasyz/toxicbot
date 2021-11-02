from __future__ import annotations

from dataclasses import dataclass

import spotipy
from spotipy import SpotifyOAuth, CacheHandler

from toxic.repositories.settings import SettingsRepository

SCOPES = [
    'user-read-playback-state',
    'user-modify-playback-state'
]


@dataclass
class Device:
    name: str
    device_id: str


class Cache(CacheHandler):
    def __init__(self, settings_repo: SettingsRepository):
        self.settings_repo = settings_repo

    def get_cached_token(self):
        return self.settings_repo.spotify_get_token()

    def save_token_to_cache(self, token_info):
        self.settings_repo.spotify_set_token(token_info)


class Spotify:
    def __init__(self, auth: SpotifyOAuth, client: spotipy.Spotify):
        self.auth = auth
        self.client = client

    @staticmethod
    def new(client_id: str, client_secret: str, settings_repo: SettingsRepository) -> Spotify:
        auth = SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri='https://slasyz.ru/',
            scope=' '.join(SCOPES),
            open_browser=False,
            cache_handler=Cache(settings_repo),
        )
        client = spotipy.Spotify(auth_manager=auth)
        return Spotify(auth, client)

    def get_auth_url(self):
        return self.auth.get_authorize_url()

    def authenticate(self, redirect_url: str):
        code = self.auth.parse_response_code(redirect_url)
        return self.auth.get_access_token(code=code)

    def is_authenticated(self):
        token = self.auth.cache_handler.get_cached_token()
        if token is None:
            return None
        token = self.auth.refresh_access_token(token['refresh_token'])
        return token is not None

    def get_devices(self) -> list[Device]:
        devices = self.client.devices()
        return [Device(device['name'], device['id']) for device in devices['devices']]

    def add_to_queue(self, uri: str, device_id: str):
        self.client.add_to_queue(uri, device_id)