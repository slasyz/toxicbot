from typing import List

import telegram


class Command:
    def handle(self, message: telegram.Message, args: List[str]):
        raise NotImplementedError()
