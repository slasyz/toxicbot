import telegram


class Handler:
    def pre_handle(self, message: telegram.Message):
        pass

    def handle(self, message: telegram.Message) -> bool:
        raise NotImplementedError()
