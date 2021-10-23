from __future__ import annotations

import re
import traceback

import requests
from loguru import logger
from lxml import html

URL = 'https://baneks.ru/random'
PREFIX_REGEXP = re.compile(r'^Анек #\d+\s+')


class Joker:
    def __init__(self, error_reply: str):
        self.error_reply = error_reply

    def get_random_joke(self) -> tuple[str, bool]:
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
            logger.opt(exception=ex).error('HTTP error when getting joke.')
            return self.error_reply, False

        if not text.startswith('Анек #'):
            logger.error('Invalid joke format.', data=data)
            return self.error_reply, False

        text = PREFIX_REGEXP.sub('', text)
        return text, True
