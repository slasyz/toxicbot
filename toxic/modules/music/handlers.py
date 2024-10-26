import aiogram
from loguru import logger

from toxic.messenger.message import PhotoMessage, TextMessage
from toxic.helpers import decorators
from toxic.modules.music.generator.links import get_hostname, extract_music_links
from toxic.modules.music.generator.generator import MusicMessageGenerator
from toxic.interfaces import CallbackHandler, MessageHandler
from toxic.messenger.message import Message, CallbackReply
from toxic.messenger.messenger import Messenger


class MusicPlaintextCallback(CallbackHandler):
    def __init__(self, music_formatter: MusicMessageGenerator, messenger: Messenger, error_reply: str):
        self.music_formatter = music_formatter
        self.messenger = messenger
        self.error_reply = error_reply

    async def handle(self, callback: aiogram.types.CallbackQuery, message: aiogram.types.Message, args: dict) -> Message | CallbackReply | None:
        link = args['link']
        music_message = await self.music_formatter.get_message(link, True)
        if music_message is None:
            logger.error('Got nothing in MusicPlaintextCallback.', link=link)
            return CallbackReply(self.error_reply)

        if message.photo is not None:  # TODO: validate this
            await self.messenger.edit_caption(message.chat.id, message.message_id, music_message.text, music_message.buttons, is_html=True)
        else:
            await self.messenger.edit_text(message.chat.id, message.message_id, music_message.text, music_message.buttons, is_html=True)

        return None


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
