import re
import traceback
from typing import Tuple

import requests
from lxml import html

URL = 'https://baneks.ru/random'
PREFIX_REGEXP = re.compile(r'^Анек #\d+\s+')


class Joker:
    def __init__(self, error_reply: str):
        self.error_reply = error_reply

    def get_random_joke(self) -> Tuple[str, bool]:
        try:
            with requests.get(URL) as req:
                data = req.content.decode('utf-8', 'ignore')
                parser = html.HTMLParser(encoding='utf-8')
                document = html.document_fromstring(data, parser=parser)
                text = document.find('.//*[@class="anek-view"]//article').text_content().strip().replace('            ', '')
        except requests.HTTPError as ex:  # обрабатывать нормально
            traceback.print_stack()
            print(ex)
            return self.error_reply, False

        if not text.startswith('Анек #'):
            # TODO: sentry
            print('!!!!!!!  кривой анекдот !!!!!!!')
            print(data)
            print('!!!!!!! /кривой анекдот !!!!!!!')
            return self.error_reply, False

        text = PREFIX_REGEXP.sub('', text)
        return text, True


class JokerFactory:
    @staticmethod
    def create(replies: dict[str, str]) -> Joker:
        return Joker(replies['error'])
