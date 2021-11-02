import json
from typing import Optional
from urllib.parse import urlencode

import requests
from loguru import logger

from toxic.features.music.structs import Type, Service, Info


class UnknownTypeException(Exception):
    pass


ODESLI_KEY_TO_SERVICE = {
    'appleMusic': Service.APPLE_MUSIC,
    'spotify': Service.SPOTIFY,
    'yandex': Service.YANDEX,
    'youtube': Service.YOUTUBE,
}


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

        result = Info(
            type=cls.str_to_type(raw_info['type']),
            artist_name=raw_info['artistName'],
            title=raw_info['title'],
            links={},
            thumbnail_url=raw_info.get('thumbnailUrl')
        )

        links = data['linksByPlatform']
        for key, service in ODESLI_KEY_TO_SERVICE.items():
            el = links.get(key)
            if el is not None:
                result.links[service] = el['url']

        return result

    def get_info(self, url: str) -> Optional[Info]:
        basepath = 'https://api.song.link/v1-alpha.1/links'
        params = {
            'url': url
        }
        url = '{}?{}'.format(basepath, urlencode(params))

        with requests.get(url) as resp:
            try:
                parsed = json.loads(resp.content)
            except json.JSONDecodeError as ex:
                logger.opt(exception=ex).error('Cannot parse Odesli response.', result=resp.content)
                return None

            try:
                return self.parse_result(parsed)
            except Exception as ex:
                logger.opt(exception=ex).error('Cannot get music info.', exc_info=ex, result=parsed)
                return None
