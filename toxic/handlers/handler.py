import telegram

from toxic.messenger.message import Message, CallbackReply


class MessageHandler:
    def handle(self, text: str, message: telegram.Message) -> str | list[Message] | None:
        raise NotImplementedError()


class CommandHandler:
    def handle(self, text: str, message: telegram.Message, args: list[str]) -> str | list[Message] | None:
        raise NotImplementedError()

    @staticmethod
    def is_admins_only() -> bool:
        return False


class CallbackHandler:
    def handle(self, callback: telegram.CallbackQuery, message: telegram.Message, args: dict) -> Message | CallbackReply | None:
        raise NotImplementedError()

    @staticmethod
    def is_admins_only() -> bool:
        return False
