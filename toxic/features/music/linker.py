from typing import Optional

from toxic.features.music.odesli import Odesli
from toxic.features.music.structs import Info


class Linker:
    def __init__(self, odesli: Odesli):
        self.odesli = odesli

    def get_info(self, url: str) -> Optional[Info]:
        # TODO: first step — get name/urls using URL
        # TODO: second step — get urls from Spotify/Yandex using name
        # TODO: third step — get urls using URLs[2] - URLs[1]

        # Boom: link -> name
        # Spotify: name -> link
        # Yandex: name -> link
        # Odesli: link -> info
        # Spotify: name -> info (необязательно)

        return self.odesli.get_info(url)
