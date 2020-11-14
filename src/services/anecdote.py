import re
import traceback

import requests
from lxml import html

URL = 'https://baneks.ru/random'


def get_random_adecdote() -> str:
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

    text = re.sub(r'^Анек #\d+\s+', '', text)
    return text
