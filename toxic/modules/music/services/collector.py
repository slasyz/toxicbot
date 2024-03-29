from loguru import logger

from toxic.modules.music.services.structs import Info, Infoer, Searcher, Service


class MusicInfoCollector:
    def __init__(self, infoers: list[Infoer], searchers: list[Searcher]):
        self.infoers = infoers
        self.searchers = searchers

    async def _collect_info_by_url(self, info: Info, url: str) -> Info:
        for infoer in self.infoers:
            new_info = await infoer.get_info(url)
            logger.debug(
                'MusicInfoCollector: infoer returned new_info.',
                url=url,
                infoer=infoer.__class__.__name__,
                new_info=new_info,
            )
            if new_info is None:
                continue

            if info.type is None:
                info.type = new_info.type
            elif new_info.type != info.type:
                # Got different entity type, ignoring it (because first one has bigger priority).
                continue

            info.artist_name = info.artist_name or new_info.artist_name
            info.title = info.title or new_info.title
            info.thumbnail_url = info.thumbnail_url or new_info.thumbnail_url
            info.links = new_info.links | info.links  # info.links wins here

            logger.debug('After infoer there is this info.', infoer=infoer.__class__.__name__, info=info)

        return info

    async def collect_info(self, url: str) -> Info | None:
        # First step — get name/urls using source URL
        info = await self._collect_info_by_url(Info(), url)
        if info.type is None:
            # At this moment we should have something.
            return None

        # Second step — get more urls from Spotify/Yandex using name
        more_urls: dict[Service, str] = {}
        for searcher in self.searchers:
            res = searcher.get_link(info.type, info.artist_name, info.title)
            if res is None:
                continue

            more_urls[res.service] = res.link

        # Third step — get even more urls using new URLs
        for new_url in more_urls.values():
            info = await self._collect_info_by_url(info, new_url)

        if info.type is None:
            return None

        info.links = more_urls | info.links

        if len(info.links) == 1 and Service.YOUTUBE in info.links:
            # That's just a YouTube video.
            return None

        return info
