from dataclasses import dataclass
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
    type: Type
    artist_name: str
    title: str

    links: dict[Service, str]
    thumbnail_url: Optional[str]
