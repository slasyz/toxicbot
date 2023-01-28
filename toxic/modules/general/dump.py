import json

import aiogram
from loguru import logger

from toxic.interfaces import CommandHandler
from toxic.messenger.message import Message
from toxic.repositories.messages import MessagesRepository


class DumpCommand(CommandHandler):
    def __init__(self, messages_repo: MessagesRepository):
        self.messages_repo = messages_repo

    @staticmethod
    def is_admins_only() -> bool:
        return True

    async def handle(self, text: str, message: aiogram.types.Message, args: list[str]) -> str | list[Message] | None:
        if len(args) != 2:
            return f'Нужно писать так: /{args[0]} UPDATE_ID'

        try:
            update_id = int(args[1])
        except ValueError:
            return f'Нужно писать так: /{args[0]} UPDATE_ID'

        dump = await self.messages_repo.get_update_dump(update_id)
        if dump is None:
            return 'В базе нет такого апдейта.'

        try:
            return json.dumps(json.loads(dump), indent=2, ensure_ascii=False)
        except json.decoder.JSONDecodeError as ex:
            logger.opt(exception=ex).error('Caught exception when decoding dump.')
            return dump
