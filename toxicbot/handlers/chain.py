from datetime import datetime

import telegram

from toxicbot import db
from toxicbot.handlers.handler import Handler
from toxicbot.helpers import messages
from toxicbot.features.chain.chain import Chain, Featurizer, Markov
from toxicbot.features.chain.splitters import PunctuationSplitter


class ChainHandler(Handler):
    def __init__(self, window: int, chain: Chain):
        self.chats: dict[int, Markov] = {}
        self.window = window
        self.chain = chain

        # TODO: move to factory, use ChainsMap
        with db.conn, db.conn.cursor() as cur:
            cur.execute('''SELECT tg_id, chain_period FROM chats''')
            for record in cur:
                self.chats[record[0]] = Markov(self.window)
                # self.chats[record[0]] = Chain(machine=self.method, featurizer=self.featurizer, splitter=self.splitter)

            # TODO: игнорировать изменения сообщений
            cur.execute('''
                SELECT chat_id, text 
                FROM messages 
                WHERE chat_id < 0 AND update_id IS NOT NULL 
                ORDER BY tg_id
            ''')
            for record in cur:
                try:
                    machine = self.chats[record[0]]
                except KeyError:
                    # TODO: MachineFactory
                    machine = Markov(self.window)
                    self.chats[record[0]] = machine

                self.chain.teach(machine, record[1])

    def _get_period(self, chat_id: int):
        with db.conn, db.conn.cursor() as cur:
            cur.execute('''SELECT chain_period FROM chats WHERE tg_id = %s''', (chat_id,))
            record = cur.fetchone()
            return record[0]

    def pre_handle(self, message: telegram.Message):
        if message.chat_id > 0:
            return

        try:
            machine = self.chats[message.chat_id]
        except KeyError:
            machine = Markov(self.window)
            self.chats[message.chat_id] = machine

        self.chain.teach(machine, message.text)

    def handle(self, message: telegram.Message) -> bool:
        if message.chat_id > 0:
            return False

        if messages.is_reply_or_mention(message):
            machine = self.chats[message.chat_id]
            text = self.chain.predict_not_empty(machine, message.text)
            messages.reply(message, text)
            return True

        if message.date.timestamp() < datetime.utcnow().timestamp() - 60:
            return False

        with db.conn, db.conn.cursor() as cur:
            cur.execute('''SELECT count(tg_id) FROM messages WHERE chat_id = %s''', (message.chat_id,))
            record = cur.fetchone()
            count = record[0]

            if count % self._get_period(message.chat_id) == 0:
                machine = self.chats[message.chat_id]
                text = self.chain.predict_not_empty(machine, message.text)
                messages.send(message.chat_id, text)
                return True

        return False


def __main__():
    import main  # pylint: disable=import-outside-toplevel
    main.init(['../../config.json'])

    # splitter = NoPunctuationSplitter()
    splitter = PunctuationSplitter()
    chain = Chain(Featurizer(), splitter)
    handler = ChainHandler(window=3, chain=chain)

    print(splitter.split("Hello, I'm a string!!! слово ещё,,, а-за-за"))
    # print(handler.chats[-362750796].data)

    for x in range(20):  # pylint: disable=unused-variable
        machine = handler.chats[-362750796]
        print('[' + chain.predict_not_empty(machine, 'Чисто') + ']')


if __name__ == '__main__':
    __main__()