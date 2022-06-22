import aiogram

from toxic.features.music.generator.generator import MusicMessageGenerator
from toxic.features.music.generator.links import get_hostname, extract_music_links
from toxic.handlers.handler import MessageHandler
from toxic.helpers import decorators
from toxic.messenger.message import Message, PhotoMessage, TextMessage


class MusicHandler(MessageHandler):
    def __init__(self, music_formatter: MusicMessageGenerator):
        self.music_formatter = music_formatter

    @decorators.non_empty
    async def handle(self, text: str, message: aiogram.types.Message) -> str | list[Message] | None:
        # pylint: disable=W0221
        # Because of the decorator
        links = extract_music_links(text)
        if not links:
            return None

        replies: list[Message] = []

        for source_link in links:
            music_message = await self.music_formatter.get_message(source_link, include_plaintext_links=False)
            if music_message is None:
                replies.append(TextMessage(f'Вижу ссылку (на {get_hostname(source_link)}), но мне нечего ответить.'))
                continue

            if music_message.image_url is not None:
                replies.append(PhotoMessage(
                    photo=music_message.image_url,
                    text=music_message.text,
                    markup=music_message.buttons,
                    is_html=True,
                ))
            else:
                replies.append(TextMessage(
                    text=music_message.text,
                    markup=music_message.buttons,
                    is_html=True,
                ))

        return replies
