import asyncio
from typing import Callable

import aiogram
from aiogram.exceptions import TelegramMigrateToChat, TelegramUnauthorizedError, TelegramBadRequest
from loguru import logger

from toxic.db import Database
from toxic.helpers import consts_tg
from toxic.helpers.delayer import DelayerFactory
from toxic.messenger.message import TextMessage, Message
from toxic.modules.dus.dus import DatabaseUpdateSaver
from toxic.repositories.users import UsersRepository

SYMBOLS_PER_SECOND = 20
MAX_DELAY = 4
DELAY_KEEPALIVE = 5


class Messenger:
    def __init__(self,
                 bot: aiogram.Bot,
                 database: Database,
                 users_repo: UsersRepository,
                 dus: DatabaseUpdateSaver,
                 delayer_factory: DelayerFactory):
        self.bot = bot
        self.database = database
        self.chain_migrate: Callable[[int, int], None] | None = None
        self.users_repo = users_repo
        self.dus = dus
        self.delayer_factory = delayer_factory

    def set_chain_migrate(self, chain_migrate: Callable[[int, int], None]):
        self.chain_migrate = chain_migrate

    async def send(self, chat_id: int, msg: str | Message, reply_to: int | None = None):
        if isinstance(msg, str):
            msg = TextMessage(msg)

        if msg.get_with_delay():
            length = msg.get_length()
            total_delay = min(length // SYMBOLS_PER_SECOND, MAX_DELAY)

            delayer = self.delayer_factory.create(total_delay, DELAY_KEEPALIVE)
            for interval in delayer:
                await self.bot.send_chat_action(chat_id, msg.get_chat_action())
                await asyncio.sleep(interval)

        # Let's make several attempts to send the message
        for _ in range(10):
            try:
                message = await msg.send(self.bot, chat_id, reply_to)
                if message is not None:
                    await self.dus.handle_message(message)
                return
            except TelegramMigrateToChat as ex:
                # We already migrated everything to the new chat
                # Let's just send the message (try again) to the new chat
                chat_id = ex.migrate_to_chat_id
                continue
            except TelegramUnauthorizedError as ex:
                # User has removed or blocked the bot.
                logger.opt(exception=ex).info('Unauthorized.', chat_id=chat_id)
                await self.database.exec('UPDATE chats SET joke_period=0 WHERE tg_id=$1', (chat_id,))
                # Don't try to send the message again
                break
        else:
            raise Exception(f'Too much ChatMigrated errors (chat_id = {chat_id}).')

    async def send_to_admins(self, msg: str | Message):
        for (id,) in await self.database.query('SELECT tg_id FROM users WHERE admin'):
            await self.send(id, msg)

    async def delete_message(self, chat_id: int, message_id: int, ignore_not_found: bool = True):
        try:
            await self.bot.delete_message(chat_id, message_id)
        except TelegramBadRequest as ex:
            if ignore_not_found and ex.label == 'Message to delete not found':
                return
            raise

    async def is_reply_or_mention(self, message: aiogram.types.Message) -> bool:
        if message.reply_to_message is not None and \
                message.reply_to_message.from_user is not None and \
                message.reply_to_message.from_user.id == self.bot.id:
            return True

        if message.text is None:
            return False

        if message.entities is None:
            return False

        for entity in message.entities:
            if entity.type == consts_tg.MESSAGEENTITY_MENTION and message.text[entity.offset:entity.offset + entity.length] == '@' + ((await self.bot.me()).username or ''):
                return True

        return False

    async def edit_text(self, chat_id: int, message_id: int, text: str, markup: aiogram.types.InlineKeyboardMarkup, is_html: bool = False):
        if len(text) > consts_tg.MAX_MESSAGE_LENGTH:
            text = text[:consts_tg.MAX_MESSAGE_LENGTH]
        await self.bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=text,
            reply_markup=markup,
            parse_mode=consts_tg.PARSEMODE_HTML if is_html else None
        )

    async def edit_caption(self, chat_id: int, message_id: int, text: str, markup: aiogram.types.InlineKeyboardMarkup, is_html: bool = False):
        if len(text) > consts_tg.MAX_CAPTION_LENGTH:
            text = text[:consts_tg.MAX_CAPTION_LENGTH]
        await self.bot.edit_message_caption(
            chat_id=chat_id,
            message_id=message_id,
            caption=text,
            reply_markup=markup,
            parse_mode=consts_tg.PARSEMODE_HTML if is_html else None
        )

    async def answer_callback(self, callback_id: str, text: str, show_alert: bool = False):
        await self.bot.answer_callback_query(callback_id, text, show_alert)


async def __main__():
    import main  # pylint: disable=import-outside-toplevel

    deps = await main.init(['../../config.json'])

    asyncio.run(deps.messenger.send(-328967401, 'приветики'))


if __name__ == '__main__':
    asyncio.run(__main__())
