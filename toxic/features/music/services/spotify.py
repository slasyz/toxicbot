from __future__ import annotations

import asyncio
import concurrent.futures
import re
from dataclasses import dataclass

import spotipy
from loguru import logger
from spotipy import SpotifyOAuth, CacheHandler, SpotifyException

from toxic.features.music.services.structs import Searcher, Type, Service, SearchResult
from toxic.repositories.settings import SettingsRepository

SCOPES = [
    'user-read-playback-state',
    'user-modify-playback-state'
]


# TODO: I am very tired right now and probably fix this later
CLEAN_REGEXP = re.compile(r"([^\w'-]\s)+")


@dataclass
class Device:
    name: str
    device_id: str


class Cache(CacheHandler):
    def __init__(self, settings_repo: SettingsRepository):
        self.settings_repo = settings_repo
        # TODO: very bad way to do this, but I don't want to refactor it properly now.
        self.pool = concurrent.futures.ThreadPoolExecutor()

    def get_cached_token(self):
        return self.pool.submit(asyncio.run, self.settings_repo.spotify_get_token())

    def save_token_to_cache(self, token_info):
        self.pool.submit(asyncio.run, self.settings_repo.spotify_set_token(token_info))


class Spotify:
    def __init__(self, auth_manager: SpotifyOAuth, cache_handler: CacheHandler, client: spotipy.Spotify):
        self.auth_manager = auth_manager
        self.cache_handler = cache_handler
        self.client = client

    @staticmethod
    def new(client_id: str, client_secret: str, settings_repo: SettingsRepository) -> Spotify:
        cache_handler = Cache(settings_repo)

        auth_manager = SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri='https://slasyz.ru/',
            scope=' '.join(SCOPES),
            open_browser=False,
            cache_handler=cache_handler,
        )

        client = spotipy.Spotify(
            auth_manager=auth_manager,
        )

        return Spotify(auth_manager, cache_handler, client)

    def create_searcher(self) -> SpotifySearcher:
        return SpotifySearcher(self.auth_manager, self.client)

    def get_auth_url(self) -> str:
        return self.auth_manager.get_authorize_url()

    def authenticate(self, redirect_url: str):
        code = self.auth_manager.parse_response_code(redirect_url)
        return self.auth_manager.get_access_token(code=code)

    def is_authenticated(self) -> bool:
        token = self.cache_handler.get_cached_token()
        if token is None:
            return False

        try:
            token = self.auth_manager.refresh_access_token(token['refresh_token'])
        except SpotifyException as ex:
            logger.opt(exception=ex).error('Error refreshing access token.')
            return False

        return token is not None


class SpotifySearcher(Searcher):
    def __init__(self, auth: SpotifyOAuth, client: spotipy.Spotify):
        self.auth = auth
        self.client = client

    def clean(self, query: str) -> str:
        return CLEAN_REGEXP.sub('', query)

    def _search(self, query: str, type: str, key: str) -> str | None:
        query = self.clean(query)

        try:
            res = self.client.search(query, type=type)
        except SpotifyException as ex:
            logger.opt(exception=ex).error('Error searching in Spotify.')
            return None
        if res is None:
            return None

        try:
            return res[key]['items'][0]['external_urls']['spotify']
        except (IndexError, KeyError, TypeError):
            # TODO: log
            return None

    def _get_link_artist(self, name: str) -> str | None:
        return self._search('{}'.format(name), 'artist', 'artists')

    def _get_link_album(self, artist_name: str, title: str) -> str | None:
        return self._search('{} {}'.format(artist_name, title), 'album', 'albums')

    def _get_link_song(self, artist_name: str, title: str) -> str | None:
        return self._search('{} {}'.format(artist_name, title), 'track', 'tracks')

    def get_link(self, type: Type, artist_name: str, title: str) -> SearchResult | None:
        res = None
        if type == Type.ARTIST:
            res = self._get_link_artist(artist_name)
        elif type == Type.ALBUM:
            res = self._get_link_album(artist_name, title)
        elif type == Type.SONG:
            res = self._get_link_song(artist_name, title)

        if res is not None:
            return SearchResult(Service.SPOTIFY, res)

        return None
