from typing import List

import telegram

from src.handlers.commands.command import Command
from src.helpers import general
from src.features.anecdote import get_random_adecdote


class AnecdoteCommand(Command):
    def handle(self, message: telegram.Message, args: List[str]):
        text = get_random_adecdote()
        general.reply(message, text)
