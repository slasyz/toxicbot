from typing import List

import telegram

from toxicbot.handlers.commands.command import Command
from toxicbot.helpers import messages
from toxicbot.features.joke import get_random_joke


class JokeCommand(Command):
    def handle(self, message: telegram.Message, args: List[str]):
        text, _ = get_random_joke()
        messages.reply(message, text)
