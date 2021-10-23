import json

import telegram
from loguru import logger

from toxic.handlers.commands.command import Command
from toxic.messenger.messenger import Messenger
from toxic.repositories.messages import MessagesRepository


class DumpCommand(Command):
    def __init__(self, messages_repo: MessagesRepository, messenger: Messenger):
        self.messages_repo = messages_repo
        self.messenger = messenger

    def handle(self, text: str, message: telegram.Message, args: list[str]):
        if len(args) != 2:
            self.messenger.reply(message, f'Нужно писать так: /{args[0]} UPDATE_ID')
            return

        try:
            update_id = int(args[1])
        except ValueError:
            self.messenger.reply(message, f'Нужно писать так: /{args[0]} UPDATE_ID')
            return

        dump = self.messages_repo.get_update_dump(update_id)
        if dump is None:
            self.messenger.reply(message, 'В базе нет такого апдейта.')
            return

        try:
            self.messenger.reply(message, json.dumps(json.loads(dump), indent=2, ensure_ascii=False))
        except json.decoder.JSONDecodeError as ex:
            logger.opt(exception=ex).error('Caught exception when decoding dump.')
            self.messenger.reply(message, dump)
