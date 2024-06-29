import json

import aiogram
from loguru import logger

from toxic.db import Database
from toxic.interfaces import CommandHandler
from toxic.messenger.message import Message


class DumpCommand(CommandHandler):
    def __init__(self, database: Database):
        self.database = database

    @staticmethod
    def is_admins_only() -> bool:
        return True

    async def _get_update_dump(self, update_id: int) -> str | None:
        row = await self.database.query_row('SELECT json FROM updates WHERE tg_id=$1', (update_id,))
        if row is None:
            return None

        return row[0]

    async def handle(self, text: str, message: aiogram.types.Message, args: list[str]) -> str | list[Message] | None:
        if len(args) != 2:
            return f'Нужно писать так: /{args[0]} UPDATE_ID'

        try:
            update_id = int(args[1])
        except ValueError:
            return f'Нужно писать так: /{args[0]} UPDATE_ID'

        dump = await self._get_update_dump(update_id)
        if dump is None:
            return 'В базе нет такого апдейта.'

        try:
            return json.dumps(json.loads(dump), indent=2, ensure_ascii=False)
        except json.decoder.JSONDecodeError as ex:
            logger.opt(exception=ex).error('Caught exception when decoding dump.')
            return dump
