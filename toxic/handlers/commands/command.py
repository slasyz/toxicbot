import telegram


class Command:
    def handle(self, text: str, message: telegram.Message, args: list[str]):
        raise NotImplementedError()
