import re
from typing import List

import telegram

from src import db
from src.handlers.commands.command import Command
from src.handlers.handler import Handler
from src.helpers import general


def get_stat(chat_id) -> str:
    with db.conn, db.conn.cursor() as cur:
        cur.execute('''
            SELECT btrim(concat(u.first_name, ' ', u.last_name)), count(m.tg_id) as c
            FROM messages m
                JOIN users u on m.user_id = u.tg_id
            WHERE chat_id=%s
            GROUP BY user_id, u.first_name, u.last_name
            ORDER BY c DESC
            LIMIT 10;
        ''', (chat_id,))

        response = ''

        for record in cur:
            response += f'\n{record[0]} — {record[1]} сообщ.'

        return response


class StatCommand(Command):
    def _get_response(self, chat_id) -> str:
        response = 'Кто сколько написал с момента запуска бота:\n'
        response += get_stat(chat_id)
        return response

    def _parse_args_and_send(self, message: telegram.Message, args: List[str]):
        try:
            chat_id = int(args[1])
        except ValueError:
            general.reply_text(message, f'Нужно писать так: /{args[0]} CHAT_ID')
            return

        response = self._get_response(chat_id)
        general.reply_text(message, response)

    def handle(self, message: telegram.Message, args: List[str]):
        if message.chat_id < 0:
            if len(args) == 1:
                response = self._get_response(message.chat_id)
                general.reply_text(message, response)
            elif len(args) == 2:
                self._parse_args_and_send(message, args)
            return

        if not general.is_admin(message.from_user.id):
            general.reply_text(message, 'Это нужно делать в общем чате, дурачок.')
            return

        if len(args) != 2:
            general.reply_text(message, f'Нужно писать так: /{args[0]} [CHAT_ID]')
            return

        self._parse_args_and_send(message, args)


PIZDIT_REGEXP = r'кто\s+больше\s+всех\s+пиздит'


class PizditHandler(Handler):
    @general.non_empty
    def handle(self, message: telegram.Message) -> bool:
        if re.search(PIZDIT_REGEXP, message.text.lower()) is None:
            return False

        response = 'Больше всех пиздят в этом чате:\n'
        response += get_stat(message.chat_id)
        general.reply_text(message, response)
        return True
