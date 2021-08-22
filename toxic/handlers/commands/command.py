import telegram


class Command:
    def handle(self, message: telegram.Message, args: list[str]):
        raise NotImplementedError()
