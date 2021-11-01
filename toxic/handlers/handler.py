import telegram


class MessageHandler:
    def pre_handle(self, message: telegram.Message):
        pass

    def handle(self, message: telegram.Message) -> bool:
        raise NotImplementedError()


class CommandHandler:
    def handle(self, text: str, message: telegram.Message, args: list[str]):
        raise NotImplementedError()

    @staticmethod
    def is_admins_only() -> bool:
        return False


class CallbackHandler:
    def handle(self, callback: telegram.CallbackQuery, message: telegram.Message, args: dict):
        raise NotImplementedError()

    @staticmethod
    def is_admins_only() -> bool:
        return False
