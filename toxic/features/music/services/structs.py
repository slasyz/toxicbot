from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


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
    type: Type = Type.ARTIST
    artist_name: str = ''
    title: str = ''

    links: dict[Service, str] = field(default_factory=dict)
    thumbnail_url: Optional[str] = None


class Infoer:
    def get_info(self, url: str) -> Optional[Info]:
        raise NotImplementedError()


@dataclass
class SearchResult:
    service: Service
    link: str


class Searcher:
    def get_link(self, type: Type, artist_name: str, title: str) -> Optional[SearchResult]:
        raise NotImplementedError()
