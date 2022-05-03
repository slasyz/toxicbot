import json
from urllib.parse import urlencode

import requests
from loguru import logger

from toxic.features.music.services.structs import Type, Service, Info, Infoer


class UnknownTypeException(Exception):
    pass


ODESLI_KEY_TO_SERVICE = {
    'appleMusic': Service.APPLE_MUSIC,
    'spotify': Service.SPOTIFY,
    'yandex': Service.YANDEX,
    'youtube': Service.YOUTUBE,
}


PREFIXES = [
    'ITUNES_SONG::',
    'DEEZER_SONG::',
    'AMAZON_SONG::',
    'YANDEX_SONG::',
]


class Odesli(Infoer):
    @staticmethod
    def _str_to_type(src: str) -> Type:
        if src == 'artist':
            return Type.ARTIST
        if src == 'album':
            return Type.ALBUM
        if src == 'song':
            return Type.SONG
        raise UnknownTypeException()

    @staticmethod
    def _change_entity_id(entity_id: str, entities: list[str]) -> str:
        for el in entities:
            for prefix in PREFIXES:
                if el.startswith(prefix):
                    return el

        return entity_id

    @classmethod
    def _parse_result(cls, data: dict) -> Info | None:
        entity_id = data.get('entityUniqueId')
        if entity_id is None:
            return None

        entities_by_id = data['entitiesByUniqueId']

        entity_id = cls._change_entity_id(entity_id, entities_by_id.keys())
        raw_info = entities_by_id[entity_id]

        result = Info(
            type=cls._str_to_type(raw_info['type']),
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

    def get_info(self, url: str) -> Info | None:
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
                return self._parse_result(parsed)
            except Exception as ex:
                logger.opt(exception=ex).error('Cannot get music info.', exc_info=ex, result=parsed)
                return None
