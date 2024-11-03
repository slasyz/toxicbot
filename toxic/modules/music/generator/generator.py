from dataclasses import dataclass

import aiogram

from toxic.modules.music.generator.content import get_content
from toxic.modules.music.services.collector import MusicInfoCollector
from toxic.repository import Repository


@dataclass
class MusicMessage:
    text: str
    buttons: aiogram.types.InlineKeyboardMarkup
    image_url: str | None


class MusicMessageGenerator:
    def __init__(self, collector: MusicInfoCollector, repo: Repository):
        self.collector = collector
        self.repo = repo

    async def get_message(
            self,
            source_link: str,
            include_plaintext_links: bool,
    ) -> MusicMessage | None:
        info = await self.collector.collect_info(source_link)
        if info is None:
            return None

        content = get_content(info)

        buttons = []
        for i, service in enumerate(content.buttons):
            button = aiogram.types.InlineKeyboardButton(text=service.name, url=service.link)
            if i % 2 == 0:
                buttons.append([button])
            else:
                buttons[-1].append(button)

        if include_plaintext_links:
            links = [f'<a href="{service.link}">{service.name}</a>' for service in content.buttons]
            content.text = f'{content.text}\n\n{" | ".join(links)}'
        else:
            buttons.append([aiogram.types.InlineKeyboardButton(
                text='📝 Пришли обычные ссылки',
                callback_data=await self.repo.insert_callback_value({
                    'name': '/music/plaintext',
                    'link': source_link,
                })
            )])

        markup = aiogram.types.InlineKeyboardMarkup(inline_keyboard=buttons)
        return MusicMessage(content.text, markup, info.thumbnail_url)
