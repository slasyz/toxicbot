import aiogram

from toxic.messenger.message import Message, CallbackReply


class MessageHandler:
    async def handle(self, text: str, message: aiogram.types.Message) -> str | list[Message] | None:
        raise NotImplementedError()


class CommandHandler:
    async def handle(self, text: str, message: aiogram.types.Message, args: list[str]) -> str | list[Message] | None:
        raise NotImplementedError()

    @staticmethod
    def is_admins_only() -> bool:
        return False


class CallbackHandler:
    async def handle(self, callback: aiogram.types.CallbackQuery, message: aiogram.types.Message, args: dict) -> Message | CallbackReply | None:
        raise NotImplementedError()

    @staticmethod
    def is_admins_only() -> bool:
        return False
