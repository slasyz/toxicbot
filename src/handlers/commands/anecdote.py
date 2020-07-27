from typing import List

import telegram

from src import helpers
from src.tasks.anecdotes import get_random_adecdote


class AnecdoteCommand:
    def handle(self, message: telegram.Message, args: List[str]):
        text = get_random_adecdote()
        helpers.reply_text(message, text)
