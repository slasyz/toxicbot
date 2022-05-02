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


def get_hostname(link: str) -> str:
    parsed = urllib.parse.urlparse(link)
    if parsed.hostname is None:
        return ''
    return parsed.hostname


def is_link_to_music(link: str) -> bool:
    hostname = get_hostname(link)
    for host in HOSTS:
        if hostname == host or hostname.endswith('.' + host):
            return True
    return False


def extract_music_links(text: str) -> list[str]:
    links = LINK_REGEXP.findall(text)
    links = [link[0] for link in links if is_link_to_music(link[0])]
    return links
