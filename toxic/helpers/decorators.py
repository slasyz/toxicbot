from typing import Callable, Awaitable

import telegram

from toxic.handlers.handler import MessageHandler
from toxic.messenger.message import Message


def non_empty(func: Callable[[MessageHandler, str, telegram.Message], Awaitable[str | list[Message] | None]]) -> Callable[[MessageHandler, str, telegram.Message], Awaitable[str | list[Message] | None]]:
    """
    Checks if message contains text before calling wrapping function.  If it does not contain it, returns False.
    """

    async def wrapper(self, text: str, message: telegram.Message):
        if message.text is None:
            return None

        return await func(self, text, message)

    return wrapper
