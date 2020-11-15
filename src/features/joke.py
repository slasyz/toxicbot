import re
import traceback

import requests
from lxml import html

URL = 'https://baneks.ru/random'
PREFIX_REGEXP = re.compile(r'^Анек #\d+\s+')


def get_random_joke() -> str:
    try:
        with requests.get(URL) as r:
            data = r.content.decode('utf-8', 'ignore')
            parser = html.HTMLParser(encoding='utf-8')
            document = html.document_fromstring(data, parser=parser)
            text = document.find('.//*[@class="anek-view"]//article').text_content().strip().replace('            ', '')
    except requests.HTTPError as e:  # обрабатывать нормально
        traceback.print_stack()
        print(e)
        return 'Хуйня какая-то.'

    if not text.startswith('Анек #'):
        print('!!!!!!!  кривой анекдот !!!!!!!')
        print(data)
        print('!!!!!!! /кривой анекдот !!!!!!!')
        return 'Я обосрался.'

    text = PREFIX_REGEXP.sub('', text)
    return text
