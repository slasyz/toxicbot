import logging

import telegram
from telegram import ReplyMarkup
from telegram.constants import CHATACTION_TYPING, CHATACTION_RECORD_VOICE

from toxic.features.voice import NextUpService


# TODO: fix problems with HTML tags
def split_into_chunks(text: str, max_len: int, max_trimmed_len: int) -> tuple[str, list[str]]:
    if len(text) <= max_len:
        return text, []
    text, rest = text[:max_len], text[max_len:]
    trimmed = [rest[i:i + max_trimmed_len] for i in range(0, len(rest), max_trimmed_len)]
    return text, trimmed


class Message:
    def get_chat_action(self) -> str:
        raise NotImplementedError()

    def get_length(self) -> int:
        raise NotImplementedError()

    def send(self, bot: telegram.Bot, chat_id: int, reply_to: int = None) -> telegram.Message:
        raise NotImplementedError()


class VoiceMessage(Message):
    def __init__(self, text, service=None):
        self.text = text
        self.service = service or NextUpService()

    def get_chat_action(self) -> str:
        return CHATACTION_RECORD_VOICE

    def get_length(self) -> int:
        return len(self.text)

    def send(self, bot: telegram.Bot, chat_id: int, reply_to: int = None) -> telegram.Message:
        try:
            f = self.service.load(self.text)
        except Exception as ex:
            logging.error('Error sending voice message.', exc_info=ex)
            return bot.send_message(chat_id,
                                    f'(Хотел записать голосовуху, не получилось)\n\n{self.text}')

        return bot.send_voice(chat_id,
                              voice=f,
                              reply_to_message_id=reply_to)


class TextMessage(Message):
    def __init__(self, text, is_html: bool = False, markup: ReplyMarkup = None, send_trimmed: bool = True):
        self.text = text
        self.is_html = is_html
        self.markup = markup
        self.send_trimmed = send_trimmed

    def get_length(self) -> int:
        return len(self.text)

    def get_chat_action(self) -> str:
        return CHATACTION_TYPING

    def send(self, bot: telegram.Bot, chat_id: int, reply_to: int = None) -> telegram.Message:
        text, trimmed = split_into_chunks(
            self.text,
            telegram.constants.MAX_MESSAGE_LENGTH,
            telegram.constants.MAX_MESSAGE_LENGTH,
        )
        first_message = bot.send_message(
            chat_id,
            text,
            reply_to_message_id=reply_to,
            disable_web_page_preview=True,
            parse_mode=telegram.ParseMode.HTML if self.is_html else None,
            reply_markup=self.markup,
        )
        if self.send_trimmed:
            for text in trimmed:
                bot.send_message(
                    chat_id,
                    text=text,
                    disable_web_page_preview=True,
                    parse_mode=telegram.ParseMode.HTML if self.is_html else None,
                )
        return first_message


class PhotoMessage(Message):
    def __init__(self, photo: bytes | str, text: str = None, is_html: bool = False, markup: ReplyMarkup = None, send_trimmed: bool = True):
        self.photo = photo
        self.text = text
        self.is_html = is_html
        self.markup = markup
        self.send_trimmed = send_trimmed

    def get_length(self) -> int:
        return len(self.text or '')

    def get_chat_action(self) -> str:
        return CHATACTION_TYPING

    def send(self, bot: telegram.Bot, chat_id: int, reply_to: int = None) -> telegram.Message:
        text, trimmed = split_into_chunks(
            self.text,
            telegram.constants.MAX_CAPTION_LENGTH,
            telegram.constants.MAX_MESSAGE_LENGTH,
        )
        first_message = bot.send_photo(
            chat_id,
            photo=self.photo,
            caption=text,
            reply_to_message_id=reply_to,
            reply_markup=self.markup,
            parse_mode=telegram.ParseMode.HTML if self.is_html else None,
        )
        if self.send_trimmed:
            for text in trimmed:
                bot.send_message(
                    chat_id,
                    text=text,
                    parse_mode=telegram.ParseMode.HTML if self.is_html else None,
                )
        return first_message
