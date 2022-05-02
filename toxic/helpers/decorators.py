from typing import Callable

import telegram

from toxic.handlers.handler import MessageHandler
from toxic.messenger.message import Message


def non_empty(func: Callable[[MessageHandler, str, telegram.Message], str | list[Message] | None]) -> Callable[[MessageHandler, str, telegram.Message], str | list[Message] | None]:
    """
    Checks if message contains text before calling wrapping function.  If it does not contain it, returns False.
    """

    def wrapper(self, text: str, message: telegram.Message):
        if message.text is None:
            return None

        return func(self, text, message)

    return wrapper
