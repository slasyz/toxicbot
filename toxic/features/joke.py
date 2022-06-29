from __future__ import annotations

import asyncio
import re
import traceback

import aiohttp
from loguru import logger
from lxml import html

URL = 'https://baneks.ru/random'
PREFIX_REGEXP = re.compile(r'^Анек #\d+\s+')


class Joker:
    def __init__(self, error_reply: str):
        self.error_reply = error_reply

    async def get_random_joke(self) -> tuple[str, bool]:
        try:
            async with aiohttp.ClientSession() as session, \
                    session.get(URL) as resp:
                data = await resp.read()
                parser = html.HTMLParser(encoding='utf-8')
                document = html.document_fromstring(data, parser=parser)
                element = document.find('.//*[@class="anek-view"]//article')
                if element is None:
                    return 'Без анекдота.', False
                text = element.text_content().strip().replace('            ', '')
        except aiohttp.ClientError as ex:  # обрабатывать нормально
            traceback.print_stack()
            logger.opt(exception=ex).error('HTTP error when getting joke.')
            return self.error_reply, False

        if not text.startswith('Анек #'):
            logger.error('Invalid joke format.', data=data)
            return self.error_reply, False

        text = PREFIX_REGEXP.sub('', text)
        return text, True


async def __main__():
    joker = Joker('there is an error')
    res, _ = await joker.get_random_joke()
    print(res)


if __name__ == '__main__':
    asyncio.run(__main__())
