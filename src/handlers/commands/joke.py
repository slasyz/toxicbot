from typing import List

import telegram

from src.handlers.commands.command import Command
from src.helpers import general
from src.features.joke import get_random_joke


class JokeCommand(Command):
    def handle(self, message: telegram.Message, args: List[str]):
        text = get_random_joke()
        general.reply(message, text)
