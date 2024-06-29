import re

import aiogram

from toxic.db import Database
from toxic.interfaces import CommandHandler
from toxic.messenger.message import Message
from toxic.messenger.messenger import Messenger


class SendCommand(CommandHandler):
    def __init__(self, database: Database, messenger: Messenger):
        self.database = database
        self.messenger = messenger

    @staticmethod
    def is_admins_only() -> bool:
        return True

    async def handle(self, text: str, message: aiogram.types.Message, args: list[str]) -> str | list[Message] | None:
        if len(args) < 3:
            return f'Нужно писать так: /{args[0]} CHAT_ID MESSAGE'

        try:
            chat_id = int(args[1])
        except ValueError:
            return f'Нужно писать так: /{args[0]} CHAT_ID MESSAGE'

        not_exist = (await self.database.query_row('SELECT tg_id FROM chats WHERE tg_id=$1', (chat_id,))) is None
        if not_exist:
            return f'Не могу найти такой чат ({chat_id}).'

        prefix_regexp = re.compile(r'^/' + args[0] + r'\s+' + args[1] + r'\s+')
        text = prefix_regexp.sub('', text)
        await self.messenger.send(chat_id, text)
        return 'Готово.'
