import json
from typing import Optional

import requests
from loguru import logger
from lxml import html

from toxic.features.music.structs import MusicInfoer, Info, Type, Service


class Boom(MusicInfoer):
    def get_info(self, url: str) -> Optional[Info]:
        try:
            return self._get_info(url)
        except Exception as ex:
            logger.opt(exception=ex).error('Exception while getting Boom info.', url=url)

        return None

    def _get_info(self, url: str) -> Optional[Info]:
        data = self._get_json(url)
        if data is None:
            return None

        links = {
            Service.BOOM: url,
        }

        tracks_store = data.get('tracksStore')
        if tracks_store is not None:
            item_share = tracks_store.get('itemShare')
            if item_share is not None:
                return Info(
                    type=Type.SONG,
                    artist_name=item_share.get('artistDisplayName'),
                    title=item_share.get('name'),
                    links=links,
                )

        albums_store = data.get('albumsStore')
        if albums_store is not None:
            item_share = albums_store.get('itemShare')
            if item_share is not None:
                return Info(
                    type=Type.ALBUM,
                    artist_name=item_share.get('artistDisplayName'),
                    title=item_share.get('name'),
                    links=links,
                )

        artists_store = data.get('artistsStore')
        if artists_store is not None:
            item_share = artists_store.get('itemShare')
            if item_share is not None:
                return Info(
                    type=Type.ARTIST,
                    artist_name=item_share.get('name'),
                    links=links,
                )

        return None

    def _get_json(self, url: str) -> Optional[dict]:
        with requests.get(url) as req:
            data = req.content.decode('utf-8', 'ignore')
            parser = html.HTMLParser(encoding='utf-8')
            document = html.document_fromstring(data, parser=parser)
            element = document.find('.//script[@id="initial-mobx-state"]')
            if element is None:
                return None
            text = element.text_content().strip()
            return json.loads(text)
