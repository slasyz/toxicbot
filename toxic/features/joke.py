from __future__ import annotations

import logging
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

    @staticmethod
    def create(error: str) -> Joker:
        return Joker(error)

    def get_random_joke(self) -> Tuple[str, bool]:
        try:
            with requests.get(URL) as req:
                data = req.content.decode('utf-8', 'ignore')
                parser = html.HTMLParser(encoding='utf-8')
                document = html.document_fromstring(data, parser=parser)
                element = document.find('.//*[@class="anek-view"]//article')
                if element is None:
                    return 'Без анекдота.', False
                text = element.text_content().strip().replace('            ', '')
        except requests.HTTPError as ex:  # обрабатывать нормально
            traceback.print_stack()
            logging.error('HTTP error when getting joke', exc_info=ex)
            return self.error_reply, False

        if not text.startswith('Анек #'):
            logging.error('Invalid joke format', extra={
                'data': data,
            })
            return self.error_reply, False

        text = PREFIX_REGEXP.sub('', text)
        return text, True
