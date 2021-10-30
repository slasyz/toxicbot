import urllib.parse

import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from toxic.features.odesli import Info, Type, Odesli
from toxic.handlers.handler import MessageHandler
from toxic.helpers import decorators
from toxic.helpers.consts import LINK_REGEXP
from toxic.messenger.message import PhotoMessage, TextMessage
from toxic.messenger.messenger import Messenger

HOSTS = [
    'music.yandex.ru',
    'youtu.be',
    'youtube.com',
    'spotify.com',
    'apple.com',
]


def get_message_and_buttons(info: Info) -> tuple[str, list[tuple[str, str]]]:
    result = f'Исполнитель: <b>{info.artist_name}</b>'
    if info.type != Type.ARTIST:
        result += f'\n{info.type.value}: <b>{info.title}</b>'

    services = []

    if info.apple_music is not None:
        services.append(('Apple Music', info.apple_music))
    if info.spotify is not None:
        services.append(('Spotify', info.spotify))
    if info.yandex is not None:
        services.append(('Яндекс.Музыка', info.yandex))
    if info.youtube is not None:
        services.append(('YouTube', info.youtube))

    return result, services


def is_link_to_music(link: str) -> bool:
    parsed = urllib.parse.urlparse(link)
    if parsed.hostname is None:
        return False
    for host in HOSTS:
        if parsed.hostname == host or parsed.hostname.endswith('.' + host):
            return True
    return False


def search_links(text: str) -> list[str]:
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
    def handle(self, text: str, message: telegram.Message) -> bool:
        # pylint: disable=W0221
        # Because of the decorator
        links = search_links(text)
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
            markup = InlineKeyboardMarkup(buttons)

            if info.thumbnail_url is not None:
                self.messenger.reply(message, PhotoMessage(
                    photo=info.thumbnail_url,
                    text=text,
                    markup=markup,
                    is_html=True,
                ), with_delay=False)
            else:
                self.messenger.reply(message, TextMessage(
                    text=text,
                    markup=markup,
                    is_html=True,
                ), with_delay=False)

        return False
