import telegram

from toxic.features.emojifier import Emojifier
from toxic.handlers.handler import CommandHandler
from toxic.messenger.message import Message


class HookahCommand(CommandHandler):
    def __init__(self, emojifier: Emojifier):
        self.emojifier = emojifier

    def handle(self, text: str, message: telegram.Message, args: list[str]) -> str | list[Message] | None:
        message_src = message.reply_to_message
        if message_src is None:
            return 'Эту команду нужно присылать в ответ на сообщение.'

        text = message_src.text or message_src.caption or ''
        if text is None or text == '':
            return '???'

        return self.emojifier.generate(text)
