from typing import List

import telegram

from src.tasks.anecdotes import get_random_adecdote


class AnecdoteCommand:
    def handle(self, message: telegram.Message, args: List[str]):
        text = get_random_adecdote()
        message.reply_text(text)
