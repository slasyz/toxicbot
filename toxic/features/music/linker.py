from typing import Optional

from loguru import logger

from toxic.features.music.structs import Info, MusicInfoer, Searcher, Service


class Linker:
    def __init__(self, infoers: list[MusicInfoer], searchers: list[Searcher]):
        self.infoers = infoers
        self.searchers = searchers

    def _collect_info_by_url(self, info: Info, url: str) -> Optional[Info]:
        for infoer in self.infoers:
            new_info = infoer.get_info(url)
            logger.debug('Linker: infoer returned new_info.', url=url, infoer=infoer.__class__.__name__, new_info=new_info)
            if new_info is None:
                continue

            if info.type is None:
                info.type = new_info.type
            elif new_info.type != info.type:
                # Got different entity type, ignoring it (because first one should have bigger priority).
                continue

            info.artist_name = info.artist_name or new_info.artist_name
            info.title = info.title or new_info.title
            info.thumbnail_url = info.thumbnail_url or new_info.thumbnail_url
            info.links = new_info.links | info.links  # info.links wins here

            logger.debug('After infoer there is this info.', infoer=infoer.__class__.__name__, info=info)

        if info.type is None:
            return None

        return info

    def get_info(self, url: str) -> Optional[Info]:
        logger.debug('Linker: start first step.')

        # First step — get name/urls using source URL
        info = self._collect_info_by_url(Info(), url)
        if info is None:
            # At this moment we should have something.
            return None

        logger.debug('Linker: start second step.', info=info.__dict__)

        # Second step — get more urls from Spotify/Yandex using name
        more_urls: dict[Service, str] = {}
        for searcher in self.searchers:
            res = searcher.get_link(info.type, info.artist_name, info.title)
            if res is None:
                continue

            service, url = res
            more_urls[service] = url

        logger.debug('Linker: start third step.', more_urls=more_urls)

        # Third step — get even more urls using new URLs
        for service, new_url in more_urls.items():
            info = self._collect_info_by_url(info, new_url)

        info.links = more_urls | info.links

        logger.debug('Linker: ended.', info=info.__dict__)

        if info.type is None:
            return None

        return info
