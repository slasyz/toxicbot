from __future__ import annotations

import re
from dataclasses import dataclass

import spotipy # type: ignore
from loguru import logger
from spotipy import SpotifyOAuth, CacheHandler, SpotifyException

from toxic.modules.music.services.structs import Searcher, Type, Service, SearchResult
from toxic.modules.spotify.worker import SpotifyCacheWorker
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
    """
    Instance of this class is called automatically from spotipy library which is sync.  It causes problems when we want
    to save token to database and read from it, because we use asyncpg which is async.

    To work around this problem, this logic is implemented:
    - class Cache saves info in memory and notifies SpotifyCacheWorker about the change;
    - class SpotifyCacheWorker is called from main event loop, and saves it to database;
    - this class is a single source of modifications for tokens, so every token change must be done by calling
      save_token_to_cache().  Otherwise, changes will not be reflected in this class.

    Another solution could be moving to some async Spotify library and manage tokens manually, but they are not mature
    yet.
    """

    def __init__(self, value: dict | None, worker: SpotifyCacheWorker):
        self.value = value
        self.worker = worker

    def get_cached_token(self):
        return self.value

    def save_token_to_cache(self, token_info: dict):
        self.value = token_info
        self.worker.put(token_info)


class Spotify:
    def __init__(self, auth_manager: SpotifyOAuth, cache_handler: CacheHandler, client: spotipy.Spotify):
        self.auth_manager = auth_manager
        self.cache_handler = cache_handler
        self.client = client

    @staticmethod
    async def new(client_id: str, client_secret: str, settings_repo: SettingsRepository, worker: SpotifyCacheWorker) -> Spotify:
        cache_handler = Cache(await settings_repo.spotify_get_token(), worker)

        auth_manager = SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri='https://syrovats.ky/',
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
        # For some reason the next line throws an exception "Refresh token revoked".  Restart helps.
        # TODO: fix this
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

    def _search(self, query: str, type: str, key: str) -> str | None:
        query = CLEAN_REGEXP.sub('', query)

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
        return self._search(name, 'artist', 'artists')

    def _get_link_album(self, artist_name: str, title: str) -> str | None:
        return self._search(f'{artist_name} {title}', 'album', 'albums')

    def _get_link_song(self, artist_name: str, title: str) -> str | None:
        return self._search(f'{artist_name} {title}', 'track', 'tracks')

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
