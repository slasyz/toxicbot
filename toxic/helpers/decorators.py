from typing import Callable, Awaitable

import aiogram

from toxic.handlers.handler import MessageHandler
from toxic.messenger.message import Message


def non_empty(func: Callable[[MessageHandler, str, aiogram.types.Message], Awaitable[str | list[Message] | None]]) -> Callable[[MessageHandler, str, aiogram.types.Message], Awaitable[str | list[Message] | None]]:
    """
    Checks if message contains text before calling wrapping function.  If it does not contain it, returns False.
    """

    async def wrapper(self, text: str, message: aiogram.types.Message):
        if message.text is None:
            return None

        return await func(self, text, message)

    return wrapper
