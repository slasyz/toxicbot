import json

import aiohttp
from loguru import logger
from lxml import html

from toxic.modules.music.services.structs import Infoer, Info, Type, Service


class Boom(Infoer):
    async def get_info(self, url: str) -> Info | None:
        try:
            return await self._get_info(url)
        except Exception as ex:
            logger.opt(exception=ex).error('Exception while getting Boom info.', url=url)

        return None

    async def _get_info(self, url: str) -> Info | None:
        data = await self._get_json(url)
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

    async def _get_json(self, url: str) -> dict | None:
        async with aiohttp.ClientSession() as session, session.get(url) as req:
            parser = html.HTMLParser(encoding='utf-8')
            document = html.document_fromstring(await req.read(), parser=parser)
            element = document.find('.//script[@id="initial-mobx-state"]')
            if element is None:
                return None
            text = element.text_content().strip()
            return json.loads(text)
