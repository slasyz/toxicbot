from datetime import datetime

import telegram

from toxicbot import db
from toxicbot.features.chain.featurizer import Featurizer
from toxicbot.features.chain.textizer import Textizer
from toxicbot.handlers.handler import Handler
from toxicbot.helpers import messages
from toxicbot.features.chain.chain import MarkovChain, Chain
from toxicbot.features.chain.splitters import PunctuationSplitter


class ChainHandler(Handler):
    def __init__(self, window: int, textizer: Textizer):
        self.chats: dict[int, Chain] = {}
        self.window = window
        self.textizer = textizer

        # TODO: move to factory, use ChainsMap
        with db.conn, db.conn.cursor() as cur:
            cur.execute('''SELECT tg_id, chain_period FROM chats''')
            for record in cur:
                self.chats[record[0]] = MarkovChain(self.window)

            # TODO: игнорировать изменения сообщений
            cur.execute('''
                SELECT chat_id, text 
                FROM messages 
                WHERE chat_id < 0 AND update_id IS NOT NULL 
                ORDER BY tg_id
            ''')
            for record in cur:
                try:
                    chain = self.chats[record[0]]
                except KeyError:
                    # TODO: ChainFactory
                    chain = MarkovChain(self.window)
                    self.chats[record[0]] = chain

                self.textizer.teach(chain, record[1])

    def _get_period(self, chat_id: int):
        with db.conn, db.conn.cursor() as cur:
            cur.execute('''SELECT chain_period FROM chats WHERE tg_id = %s''', (chat_id,))
            record = cur.fetchone()
            return record[0]

    def pre_handle(self, message: telegram.Message):
        if message.chat_id > 0:
            return

        try:
            chain = self.chats[message.chat_id]
        except KeyError:
            chain = MarkovChain(self.window)
            self.chats[message.chat_id] = chain

        self.textizer.teach(chain, message.text)

    def handle(self, message: telegram.Message) -> bool:
        if message.chat_id > 0:
            return False

        if messages.is_reply_or_mention(message):
            chain = self.chats[message.chat_id]
            text = self.textizer.predict_not_empty(chain, message.text)
            messages.reply(message, text)
            return True

        if message.date.timestamp() < datetime.utcnow().timestamp() - 60:
            return False

        with db.conn, db.conn.cursor() as cur:
            cur.execute('''SELECT count(tg_id) FROM messages WHERE chat_id = %s''', (message.chat_id,))
            record = cur.fetchone()
            count = record[0]

            if count % self._get_period(message.chat_id) == 0:
                chain = self.chats[message.chat_id]
                text = self.textizer.predict_not_empty(chain, message.text)
                messages.send(message.chat_id, text)
                return True

        return False


def __main__():
    import main  # pylint: disable=import-outside-toplevel
    main.init(['../../config.json'])

    # splitter = NoPunctuationSplitter()
    splitter = PunctuationSplitter()
    textizer = Textizer(Featurizer(), splitter)
    handler = ChainHandler(window=3, textizer=textizer)

    print(splitter.split("Hello, I'm a string!!! слово ещё,,, а-за-за"))
    # print(handler.chats[-362750796].data)

    for x in range(20):  # pylint: disable=unused-variable
        chain = handler.chats[-362750796]
        print('[' + textizer.predict_not_empty(chain, 'Чисто') + ']')


if __name__ == '__main__':
    __main__()
