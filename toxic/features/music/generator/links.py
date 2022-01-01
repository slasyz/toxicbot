import urllib.parse

from toxic.helpers.consts import LINK_REGEXP


HOSTS = [
    'music.yandex.ru',
    'youtu.be',
    'youtube.com',
    'spotify.com',
    'apple.com',
    'boom.ru',
]


def is_link_to_music(link: str) -> bool:
    parsed = urllib.parse.urlparse(link)
    if parsed.hostname is None:
        return False
    for host in HOSTS:
        if parsed.hostname == host or parsed.hostname.endswith('.' + host):
            return True
    return False


def extract_music_links(text: str) -> list[str]:
    links = LINK_REGEXP.findall(text)
    links = [link[0] for link in links if is_link_to_music(link[0])]
    return links
