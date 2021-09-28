import json
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Optional
from urllib.parse import urlencode

import requests


class UnknownTypeException(Exception):
    pass


class Type(Enum):
    ARTIST = 'Исполнитель'
    ALBUM = 'Альбом'
    SONG = 'Трек'


@dataclass
class Info:
    type: Type
    artist_name: str
    title: str

    apple_music: Optional[str]
    spotify: Optional[str]
    yandex: Optional[str]
    youtube_music: Optional[str]

    thumbnail_url: Optional[str]


class Odesli:
    @staticmethod
    def str_to_type(src: str) -> Type:
        if src == 'artist':
            return Type.ARTIST
        if src == 'album':
            return Type.ALBUM
        if src == 'song':
            return Type.SONG
        raise UnknownTypeException()

    @classmethod
    def parse_result(cls, data: dict) -> Info:
        entity_id = data['entityUniqueId']
        raw_info = data['entitiesByUniqueId'][entity_id]

        links = data['linksByPlatform']

        apple_music = links.get('appleMusic')
        spotify = links.get('spotify')
        yandex = links.get('yandex')
        youtube_music = links.get('youtubeMusic')

        return Info(
            type=cls.str_to_type(raw_info['type']),
            artist_name=raw_info['artistName'],
            title=raw_info['title'],

            apple_music=apple_music['url'] if apple_music else None,
            spotify=spotify['url'] if spotify else None,
            yandex=yandex['url'] if yandex else None,
            youtube_music=youtube_music['url'] if youtube_music else None,

            thumbnail_url=raw_info.get('thumbnailUrl')
        )

    def get_info(self, link: str) -> Optional[Info]:
        basepath = 'https://api.song.link/v1-alpha.1/links'
        params = {
            'url': link
        }
        url = '{}?{}'.format(basepath, urlencode(params))

        with requests.get(url) as resp:
            try:
                parsed = json.loads(resp.content)
            except json.JSONDecodeError as ex:
                logging.error('Cannot parse Odesli response.', exc_info=ex, extra={
                    'result': resp.content,
                })
                return None

            try:
                return self.parse_result(parsed)
            except Exception as ex:
                logging.error('Cannot get music info.', exc_info=ex, extra={
                    'result': parsed
                })
                return None
