from typing import List

import telegram

from src.helpers import general
from src.helpers.anecdote import get_random_adecdote


class AnecdoteCommand:
    def handle(self, message: telegram.Message, args: List[str]):
        text = get_random_adecdote()
        general.reply_text(message, text)
