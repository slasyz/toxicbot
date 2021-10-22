import logging
from typing import Union

import telegram
from telegram import ReplyMarkup
from telegram.constants import CHATACTION_TYPING, CHATACTION_RECORD_VOICE

from toxic.features.voice import NextUpService


# TODO: если войс, то предлагаем caption, text/html, markup, прислать остаток вторым сообщением
# TODO: если картинка, то предлагаем caption, text/html, markup, прислать остаток вторым сообщением
# TODO: если текст, то предлагаем текст, text/html, markup, прислать остаток вторым сообщением


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
            return bot.send_voice(chat_id,
                                  voice=f,
                                  reply_to_message_id=reply_to)
        except Exception as ex:
            logging.error('Error sending voice message.', exc_info=ex)
            return bot.send_message(chat_id,
                                    f'(Хотел записать голосовуху, не получилось)\n\n{self.text}')


class TextMessage(Message):
    def __init__(self, text, is_html: bool = False, markup: ReplyMarkup = None):
        self.text = text
        self.is_html = is_html
        self.markup = markup

    def get_length(self) -> int:
        return len(self.text)

    def get_chat_action(self) -> str:
        return CHATACTION_TYPING

    def send(self, bot: telegram.Bot, chat_id: int, reply_to: int = None) -> telegram.Message:
        return bot.send_message(
            chat_id,
            self.text,
            reply_to_message_id=reply_to,
            disable_web_page_preview=True,
            parse_mode=telegram.ParseMode.HTML if self.is_html else None,
            reply_markup=self.markup,
        )


class PhotoMessage(Message):
    def __init__(self, photo: Union[bytes, str], text: str = None, is_html: bool = False, markup: ReplyMarkup = None):
        self.photo = photo
        self.text = text
        self.is_html = is_html
        self.markup = markup

    def get_length(self) -> int:
        return len(self.text or '')

    def get_chat_action(self) -> str:
        return CHATACTION_TYPING

    def send(self, bot: telegram.Bot, chat_id: int, reply_to: int = None) -> telegram.Message:
        return bot.send_photo(
            chat_id,
            photo=self.photo,
            caption=self.text,
            reply_to_message_id=reply_to,
            reply_markup=self.markup,
            parse_mode=telegram.ParseMode.HTML if self.is_html else None,
        )
