from dataclasses import dataclass

import aiogram.types

from toxic.helpers import consts_tg


# TODO: fix problems with HTML tags
def split_into_chunks(text: str | None, max_len: int, max_trimmed_len: int) -> tuple[str | None, list[str]]:
    if text is None:
        return None, []
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

    async def send(self, bot: aiogram.Bot, chat_id: int, reply_to: int | None = None) -> aiogram.types.Message | None:
        raise NotImplementedError()

    def get_with_delay(self) -> bool:
        return False


class TextMessage(Message):
    def __init__(self,
                 text,
                 is_html: bool = False,
                 markup: aiogram.types.InlineKeyboardMarkup | aiogram.types.ReplyKeyboardMarkup | aiogram.types.ReplyKeyboardRemove | aiogram.types.ForceReply | None = None,
                 send_trimmed: bool = True,
                 with_delay: bool = False):
        self.text = text
        self.is_html = is_html
        self.markup = markup
        self.send_trimmed = send_trimmed
        self.with_delay = with_delay

    def get_length(self) -> int:
        return len(self.text)

    def get_chat_action(self) -> str:
        return consts_tg.CHATACTION_TYPING

    def get_with_delay(self) -> bool:
        return self.with_delay

    async def send(self, bot: aiogram.Bot, chat_id: int, reply_to: int | None = None) -> aiogram.types.Message | None:
        text, trimmed = split_into_chunks(
            self.text,
            consts_tg.MAX_MESSAGE_LENGTH,
            consts_tg.MAX_MESSAGE_LENGTH,
        )
        if text is None:
            return None
        first_message = await bot.send_message(
            chat_id,
            text,
            reply_to_message_id=reply_to,
            disable_web_page_preview=True,
            parse_mode=aiogram.enums.ParseMode.HTML if self.is_html else None,
            reply_markup=self.markup,
        )
        if self.send_trimmed:
            for text in trimmed:
                await bot.send_message(
                    chat_id,
                    text=text,
                    disable_web_page_preview=True,
                    parse_mode=aiogram.enums.ParseMode.HTML if self.is_html else None,
                )
        return first_message


class PhotoMessage(Message):
    def __init__(self,
                 photo: bytes | str,
                 text: str | None = None,
                 is_html: bool = False,
                 markup: aiogram.types.InlineKeyboardMarkup | aiogram.types.ReplyKeyboardMarkup | aiogram.types.ReplyKeyboardRemove | aiogram.types.ForceReply | None = None,
                 send_trimmed: bool = True):
        self.photo = str(photo)
        self.text = text
        self.is_html = is_html
        self.markup = markup
        self.send_trimmed = send_trimmed

    def get_length(self) -> int:
        return len(self.text or '')

    def get_chat_action(self) -> str:
        return consts_tg.CHATACTION_TYPING

    async def send(self, bot: aiogram.Bot, chat_id: int, reply_to: int | None = None) -> aiogram.types.Message | None:
        text, trimmed = split_into_chunks(
            self.text,
            consts_tg.MAX_CAPTION_LENGTH,
            consts_tg.MAX_MESSAGE_LENGTH,
        )
        if self.photo is None:
            return None
        first_message = await bot.send_photo(
            chat_id,
            photo=self.photo,
            caption=text,
            reply_to_message_id=reply_to,
            reply_markup=self.markup,
            parse_mode=consts_tg.PARSEMODE_HTML if self.is_html else None,
        )
        if self.send_trimmed:
            for text in trimmed:
                await bot.send_message(
                    chat_id,
                    text=text,
                    parse_mode=consts_tg.PARSEMODE_HTML if self.is_html else None,
                )
        return first_message


@dataclass
class CallbackReply:
    text: str
    show_alert: bool = False
