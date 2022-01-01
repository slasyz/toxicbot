import telegram
from loguru import logger

from toxic.features.music.generator.generator import MusicMessageGenerator
from toxic.features.music.generator.links import extract_music_links
from toxic.handlers.handler import MessageHandler
from toxic.helpers import decorators
from toxic.messenger.message import Message, PhotoMessage, TextMessage
from toxic.messenger.messenger import Messenger


class MusicHandler(MessageHandler):
    def __init__(self, music_formatter: MusicMessageGenerator, messenger: Messenger):
        self.music_formatter = music_formatter
        self.messenger = messenger

    @decorators.non_empty
    def handle(self, text: str, message: telegram.Message) -> bool:
        # pylint: disable=W0221
        # Because of the decorator
        links = extract_music_links(text)
        if not links:
            return False

        for source_link in links:
            music_message = self.music_formatter.get_message(source_link, include_plaintext_links=False)
            if music_message is None:
                logger.warning('Got no link music info in MusicHandler.', source_link=source_link)
                continue
            response_message: Message

            if music_message.image_url is not None:
                response_message = PhotoMessage(
                    photo=music_message.image_url,
                    text=music_message.text,
                    markup=music_message.buttons,
                    is_html=True,
                )
            else:
                response_message = TextMessage(
                    text=music_message.text,
                    markup=music_message.buttons,
                    is_html=True,
                )

            self.messenger.reply(message, response_message)

        return False
