import telegram

from toxic.features.emojifier import Emojifier
from toxic.handlers.handler import CommandHandler
from toxic.messenger.messenger import Messenger


class HookahCommand(CommandHandler):
    def __init__(self, emojifier: Emojifier, messenger: Messenger):
        self.emojifier = emojifier
        self.messenger = messenger

    def handle(self, text: str, message: telegram.Message, args: list[str]):
        message_src = message.reply_to_message
        if message_src is None:
            self.messenger.reply(message, 'Эту команду нужно присылать в ответ на сообщение.')
            return

        text = text or message.caption or ''
        if text is None or text == '':
            self.messenger.reply(message, '???')
            return

        res = self.emojifier.generate(text)
        self.messenger.reply(message, res)
