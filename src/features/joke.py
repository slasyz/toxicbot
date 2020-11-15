import re
import traceback
from typing import Tuple

import requests
from lxml import html

URL = 'https://baneks.ru/random'
PREFIX_REGEXP = re.compile(r'^Анек #\d+\s+')


def get_random_joke() -> Tuple[str, bool]:
    try:
        with requests.get(URL) as req:
            data = req.content.decode('utf-8', 'ignore')
            parser = html.HTMLParser(encoding='utf-8')
            document = html.document_fromstring(data, parser=parser)
            text = document.find('.//*[@class="anek-view"]//article').text_content().strip().replace('            ', '')
    except requests.HTTPError as ex:  # обрабатывать нормально
        traceback.print_stack()
        print(ex)
        return 'Хуйня какая-то.', False

    if not text.startswith('Анек #'):
        print('!!!!!!!  кривой анекдот !!!!!!!')
        print(data)
        print('!!!!!!! /кривой анекдот !!!!!!!')
        return 'Я обосрался.', False

    text = PREFIX_REGEXP.sub('', text)
    return text, True
