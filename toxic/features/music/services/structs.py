from dataclasses import dataclass, field
from enum import Enum


class Type(Enum):
    ARTIST = 'Исполнитель'
    ALBUM = 'Альбом'
    SONG = 'Трек'


class Service(Enum):
    APPLE_MUSIC = 'Apple Music'
    SPOTIFY = 'Spotify'
    YANDEX = 'Яндекс.Музыка'
    YOUTUBE = 'YouTube'
    BOOM = 'Boom'


@dataclass
class Info:
    type: Type | None = None
    artist_name: str = ''
    title: str = ''

    links: dict[Service, str] = field(default_factory=dict)
    thumbnail_url: str | None = None


class Infoer:
    def get_info(self, url: str) -> Info | None:
        raise NotImplementedError()


@dataclass
class SearchResult:
    service: Service
    link: str


class Searcher:
    def get_link(self, type: Type, artist_name: str, title: str) -> SearchResult | None:
        raise NotImplementedError()
