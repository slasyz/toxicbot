import telegram


class MessageHandler:
    def pre_handle(self, message: telegram.Message):
        pass

    def handle(self, message: telegram.Message) -> bool:
        raise NotImplementedError()


class CallbackHandler:
    def handle(self, callback: telegram.CallbackQuery, args: dict):
        raise NotImplementedError()
