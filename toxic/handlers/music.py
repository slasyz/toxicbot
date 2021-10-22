import urllib.parse
from typing import List, Tuple

import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from toxic.features.odesli import Info, Type, Odesli
from toxic.handlers.handler import MessageHandler
from toxic.helpers import decorators
from toxic.helpers.consts import LINK_REGEXP
from toxic.messenger.message import PhotoWithHTMLAndMarkupMessage
from toxic.messenger.messenger import Messenger

HOSTS = [
    'music.yandex.ru',
    'youtu.be',
    'youtube.com',
    'spotify.com',
    'apple.com',
]


def get_message_and_buttons(info: Info) -> Tuple[str, List[Tuple[str, str]]]:
    result = f'Исполнитель: <b>{info.artist_name}</b>'
    if info.type != Type.ARTIST:
        result += f'\n{info.type.value}: <b>{info.title}</b>'

    services = []

    if info.apple_music is not None:
        services.append(('Apple Music', info.apple_music))
        # services.append('<a href="{}">Apple Music</a>'.format(info.apple_music))
    if info.spotify is not None:
        services.append(('Spotify', info.spotify))
        # services.append('<a href="{}">Spotify</a>'.format(info.spotify))
    if info.yandex is not None:
        services.append(('Яндекс.Музыка', info.yandex))
        # services.append('<a href="{}">Яндекс.Музыка</a>'.format(info.yandex))
    if info.youtube is not None:
        services.append(('YouTube', info.youtube))
        # services.append('<a href="{}">YouTube Music</a>'.format(info.youtube_music))

    # if services:
    #     result += '\n\n' + ' • '.join(services)

    return result, services


def is_link_to_music(link: str) -> bool:
    parsed = urllib.parse.urlparse(link)
    for host in HOSTS:
        if parsed.hostname == host or parsed.hostname.endswith('.' + host):
            return True
    return False


def search_links(text: str) -> List[str]:
    links = LINK_REGEXP.findall(text)
    links = [link[0] for link in links if is_link_to_music(link[0])]
    return links


def get_button(text: str, url: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(text, url=url)


class MusicHandler(MessageHandler):
    def __init__(self, service: Odesli, messenger: Messenger):
        self.service = service
        self.messenger = messenger

    @decorators.non_empty
    def handle(self, message: telegram.Message) -> bool:
        links = search_links(message.text)
        if not links:
            return False

        for link in links:
            info = self.service.get_info(link)
            if info is None:
                continue

            text, services = get_message_and_buttons(info)

            buttons = []
            for i, service in enumerate(services):
                button = get_button(service[0], service[1])
                if i % 2 == 0:
                    buttons.append([button])
                else:
                    buttons[-1].append(button)

            self.messenger.reply(message, PhotoWithHTMLAndMarkupMessage(
                text=text,
                photo=info.thumbnail_url,
                markup=InlineKeyboardMarkup(buttons),
            ), with_delay=False)

        return False
