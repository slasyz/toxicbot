import telegram
from loguru import logger

from toxic.features.music.generator.generator import MusicMessageGenerator
from toxic.handlers.handler import CallbackHandler
from toxic.messenger.message import Message, CallbackReply
from toxic.messenger.messenger import Messenger


class MusicPlaintextCallback(CallbackHandler):
    def __init__(self, music_formatter: MusicMessageGenerator, messenger: Messenger, error_reply: str):
        self.music_formatter = music_formatter
        self.messenger = messenger
        self.error_reply = error_reply

    async def handle(self, callback: telegram.CallbackQuery, message: telegram.Message, args: dict) -> Message | CallbackReply | None:
        link = args['link']
        music_message = self.music_formatter.get_message(link, True)
        if music_message is None:
            logger.error('Got nothing in MusicPlaintextCallback.', link=link)
            return CallbackReply(self.error_reply)

        if message.photo is not None:  # TODO: validate this
            self.messenger.edit_caption(message.chat_id, message.message_id, music_message.text, music_message.buttons, is_html=True)
        else:
            self.messenger.edit_text(message.chat_id, message.message_id, music_message.text, music_message.buttons, is_html=True)

        return None
