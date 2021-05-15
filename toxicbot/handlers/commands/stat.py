import re

import telegram

from toxicbot.db import Database
from toxicbot.handlers.commands.command import Command
from toxicbot.handlers.handler import Handler
from toxicbot.helpers import decorators
from toxicbot.helpers.messages import Bot


def get_stat(chat_id: int, database: Database) -> str:
    rows = database.query('''
            SELECT btrim(concat(u.first_name, ' ', u.last_name)), count(m.tg_id) as c
            FROM messages m
                JOIN users u on m.user_id = u.tg_id
            WHERE chat_id=%s
            GROUP BY user_id, u.first_name, u.last_name
            ORDER BY c DESC
            LIMIT 10;
        ''', (chat_id,))

    response = ''
    for row in rows:
        response += f'\n{row[0]} — {row[1]} сообщ.'

    return response


class StatCommand(Command):
    def __init__(self, database: Database, bot: Bot):
        self.database = database
        self.bot = bot

    def _get_response(self, chat_id) -> str:
        response = 'Кто сколько написал с момента запуска бота:\n'
        response += get_stat(chat_id, self.database)
        return response

    def _parse_args_and_send(self, message: telegram.Message, args: list[str]):
        try:
            chat_id = int(args[1])
        except ValueError:
            self.bot.reply(message, f'Нужно писать так: /{args[0]} CHAT_ID')
            return

        response = self._get_response(chat_id)
        self.bot.reply(message, response)

    def handle(self, message: telegram.Message, args: list[str]):
        if message.chat_id < 0:
            if len(args) == 1:
                response = self._get_response(message.chat_id)
                self.bot.reply(message, response, delay=0)
            elif len(args) == 2:
                self._parse_args_and_send(message, args)
            return

        if not self.database.is_admin(message.from_user.id):
            self.bot.reply(message, 'Это нужно делать в общем чате, дурачок.')
            return

        if len(args) != 2:
            self.bot.reply(message, f'Нужно писать так: /{args[0]} [CHAT_ID]')
            return

        self._parse_args_and_send(message, args)


class StatsHandler(Handler):
    def __init__(self, replies: dict[re.Pattern, str], database: Database, bot: Bot):
        self.replies = replies
        self.database = database
        self.bot = bot

    @decorators.non_empty
    def handle(self, message: telegram.Message) -> bool:
        for key, value in self.replies.items():
            if key.search(message.text.lower()) is None:
                continue

            response = value + ':\n'
            response += get_stat(message.chat_id, self.database)
            self.bot.reply(message, response, delay=0)

            return True


class StatsHandlerFactory:
    def create(self, replies: dict[str, str], database: Database, bot: Bot) -> StatsHandler:
        replies_regexes: dict[re.Pattern, str] = {}

        for key, value in replies.items():
            regexp = re.compile(key)
            replies_regexes[regexp] = value

        return StatsHandler(replies_regexes, database, bot)
