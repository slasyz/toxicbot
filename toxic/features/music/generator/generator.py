from dataclasses import dataclass
from typing import Optional

from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ReplyMarkup

from toxic.features.music.generator.content import get_content
from toxic.features.music.services.collector import MusicInfoCollector
from toxic.features.music.services.structs import Type, Service
from toxic.messenger.message import Message
from toxic.repositories.callback_data import CallbackDataRepository
from toxic.repositories.settings import SettingsRepository


@dataclass
class MusicMessage:
    text: str
    buttons: ReplyMarkup
    image_url: Optional[str]


class MusicMessageGenerator:
    def __init__(self, collector: MusicInfoCollector, settings_repo: SettingsRepository, callback_data_repo: CallbackDataRepository):
        self.collector = collector
        self.settings_repo = settings_repo
        self.callback_data_repo = callback_data_repo

    def get_message(
            self,
            source_link: str,
            include_plaintext_links: bool,
    ) -> Optional[MusicMessage]:
        info = self.collector.collect_info(source_link)
        if info is None:
            return None

        content = get_content(info)

        buttons = []
        spotify_url = None
        for i, service in enumerate(content.buttons):
            button = InlineKeyboardButton(service.name, url=service.link)
            if i % 2 == 0:
                buttons.append([button])
            else:
                buttons[-1].append(button)

            if service.name == Service.SPOTIFY.value:
                spotify_url = service.link

        if info.type == Type.SONG and self.settings_repo.is_spotify_enabled() and spotify_url is not None:
            buttons.append([InlineKeyboardButton(
                '➡️ 🎷',
                callback_data=self.callback_data_repo.insert_value({
                    'name': '/spotify/enqueue',
                    'url': spotify_url,
                }),
            )])

        if include_plaintext_links:
            links = [f'<a href="{service.link}">{service.name}</a>' for service in content.buttons]
            content.text = '{}\n\n{}'.format(content.text, ' | '.join(links))
        else:
            buttons.append([InlineKeyboardButton(
                '📝 Пришли обычные ссылки',
                callback_data=self.callback_data_repo.insert_value({
                    'name': '/music/plaintext',
                    'link': source_link,
                })
            )])

        markup = InlineKeyboardMarkup(buttons)
        return MusicMessage(content.text, markup, info.thumbnail_url)

    def get_message_plaintext(self) -> Message:
        ...
