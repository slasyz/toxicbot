import asyncio

import telegram
from loguru import logger
from telegram import ReplyMarkup
from telegram.constants import MESSAGEENTITY_MENTION
from telegram.error import BadRequest, ChatMigrated, Unauthorized

from toxic.handlers.database import DatabaseUpdateSaver
from toxic.helpers.delayer import DelayerFactory
from toxic.messenger.message import TextMessage, Message
from toxic.repositories.chats import CachedChatsRepository
from toxic.repositories.users import UsersRepository

SYMBOLS_PER_SECOND = 20
MAX_DELAY = 4
DELAY_KEEPALIVE = 5


class Messenger:
    def __init__(self, bot: telegram.Bot, chats_repo: CachedChatsRepository, users_repo: UsersRepository, dus: DatabaseUpdateSaver, delayer_factory: DelayerFactory):
        self.bot = bot
        self.chats_repo = chats_repo
        self.users_repo = users_repo
        self.dus = dus
        self.delayer_factory = delayer_factory

    async def send(self, chat_id: int, msg: str | Message, reply_to: int = None):
        if isinstance(msg, str):
            msg = TextMessage(msg)

        if msg.get_with_delay():
            length = msg.get_length()
            total_delay = min(length // SYMBOLS_PER_SECOND, MAX_DELAY)

            delayer = self.delayer_factory.create(total_delay, DELAY_KEEPALIVE)
            for interval in delayer:
                self.bot.send_chat_action(chat_id, msg.get_chat_action())
                await asyncio.sleep(interval)

        chat_id = self.chats_repo.get_latest_chat_id(chat_id)

        for _ in range(10):
            try:
                message = msg.send(self.bot, chat_id, reply_to)
                self.dus.handle_message(message)
                return
            except ChatMigrated as ex:
                logger.info('Chat migrated.', chat_id=chat_id, new_chat_id=ex.new_chat_id)
                self.chats_repo.update_next_id(chat_id, ex.new_chat_id)
                self.chats_repo.disable_joke(chat_id)
                chat_id = ex.new_chat_id
                continue
            except Unauthorized as ex:
                logger.opt(exception=ex).info('Unauthorized.', chat_id=chat_id)
                self.chats_repo.disable_joke(chat_id)
            break
        else:
            raise Exception('Too much ChatMigrated errors (chat_id = {}).'.format(chat_id))

    async def send_to_admins(self, msg: str | Message):
        for id in self.users_repo.get_admins():
            await self.send(id, msg)

    def delete_message(self, chat_id: int, message_id: int, ignore_not_found: bool = True):
        try:
            self.bot.delete_message(chat_id, message_id)
        except BadRequest as ex:
            if ignore_not_found and ex.message == 'Message to delete not found':
                return
            raise

    def is_reply_or_mention(self, message: telegram.Message) -> bool:
        if message.reply_to_message is not None and \
                message.reply_to_message.from_user is not None and \
                message.reply_to_message.from_user.id == self.bot.id:
            return True

        if message.text is None:
            return False

        for entity in message.entities:
            if entity.type == MESSAGEENTITY_MENTION and message.text[entity.offset:entity.offset + entity.length] == '@' + self.bot.username:
                return True

        return False

    def edit_text(self, chat_id: int, message_id: int, text: str, markup: ReplyMarkup, is_html: bool = False):
        if len(text) > telegram.constants.MAX_MESSAGE_LENGTH:
            text = text[:telegram.constants.MAX_MESSAGE_LENGTH]
        self.bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=text,
            reply_markup=markup,
            parse_mode=telegram.ParseMode.HTML if is_html else None
        )

    def edit_caption(self, chat_id: int, message_id: int, text: str, markup: ReplyMarkup, is_html: bool = False):
        if len(text) > telegram.constants.MAX_CAPTION_LENGTH:
            text = text[:telegram.constants.MAX_CAPTION_LENGTH]
        self.bot.edit_message_caption(
            chat_id=chat_id,
            message_id=message_id,
            caption=text,
            reply_markup=markup,
            parse_mode=telegram.ParseMode.HTML if is_html else None
        )


def __main__():
    import main  # pylint: disable=import-outside-toplevel

    deps = main.init(['../../config.json'])

    asyncio.run(deps.messenger.send(-328967401, 'приветики'))


if __name__ == '__main__':
    __main__()
