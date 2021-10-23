import csv
import dataclasses
import hashlib
import os
from datetime import datetime
from typing import List, Tuple
from urllib.parse import urljoin

import requests
from lxml import html

from toxic.features.taro import CardData


def normalize(src: str) -> str:
    return src.replace('ё', 'е').replace('Ë', 'Е')


def get_with_cache(url: str) -> str:
    hash = hashlib.md5(url.encode('utf-8')).hexdigest()
    filepath = os.path.join(os.path.dirname(__file__), 'cache', hash + '.html')
    try:
        with open(filepath, 'r') as f:
            print('reading {} from file ({})'.format(url, hash))
            return f.read()
    except FileNotFoundError:
        pass

    with requests.get(url) as req:
        print('reading {} from url'.format(url))
        data = req.content.decode('utf-8', 'ignore')

    with open(filepath, 'w') as f:
        print('dumping {} to file ({})'.format(url, hash))
        f.write(data)

    return data


def get_cards_links() -> dict[str, str]:
    src_link = 'https://astrohelper.ru/gadaniya/taro/znachenie/'
    data = get_with_cache(src_link)
    parser = html.HTMLParser(encoding='utf-8')
    document = html.document_fromstring(data, parser=parser)
    elements = document.xpath('.//*[@class="zsign-runes2"]/parent::a')

    res = {}
    for el in elements:
        el_text = el.xpath('.//div[@class="ztext"]')[0]
        name = el_text.text.strip()
        href = el.attrib['href']
        res[name] = urljoin(src_link, href)

    return res


def get_card_content(url: str):
    data = get_with_cache(url)
    parser = html.HTMLParser(encoding='utf-8')
    document = html.document_fromstring(data, parser=parser)
    el_article = document.xpath('.//article')[0]
    lines = el_article.xpath('./*')

    result_map = {}

    current_h1 = ''
    current_h2 = ''

    for line in lines:
        if line.text is None:
            continue

        line_text = line.text.strip()
        if line_text == '':
            continue

        if line_text.endswith('Общее значение'):
            print('found general')
            current_h1 = 'general'
            current_h2 = 'forwards'
        elif line_text.endswith('Значение в любви и отношениях'):
            print('found love')
            current_h1 = 'love'
            current_h2 = ''
        elif line_text.endswith('Значение в ситуации и вопросе'):
            print('found question')
            current_h1 = 'question'
            current_h2 = ''
        elif line_text.endswith('Значение карты дня'):
            print('found daily')
            current_h1 = 'daily'
            current_h2 = ''
        elif line_text.endswith('Совет карты'):
            print('found advice')
            current_h1 = 'advice'
            current_h2 = ''
        elif line_text == 'Прямое положение':
            print('found forwards')
            current_h2 = 'forwards'
        elif line_text == 'Перевернутое положение':
            print('found backwards')
            current_h2 = 'backwards'
        elif line_text.endswith('Сочетание с другими картами'):
            print('found compatibility')
            break
        else:
            if current_h1 == '':
                raise Exception('h1 is empty')

            key = (current_h1, current_h2)
            txt = result_map.get(key, [])
            txt.append(line_text)
            print('setting to {}'.format(key))
            result_map[key] = txt

    for key, val in result_map.items():
        result_map[key] = '\n\n'.join(line.strip() for line in val)

    return result_map


def convert_map_to_table_row(map: dict[tuple[str, str], list[str]]) -> list[str]:
    row = CardData()

    if len(map) != 8:
        raise Exception('map length is not 8, but {}'.format(len(map)))

    row.general_forwards = map[('general', 'forwards')]
    row.general_backwards = map[('general', 'backwards')]
    row.love_forwards = map[('love', 'forwards')]
    row.love_backwards = map[('love', 'backwards')]
    row.question_forwards = map[('question', 'forwards')]
    row.question_backwards = map[('question', 'backwards')]
    row.daily = map[('daily', '')]
    row.advice = map[('advice', '')]

    return list(dataclasses.astuple(row))


def main():
    names = get_cards_links()
    texts = {}
    for name, link in names.items():
        print(name, link)
        map = get_card_content(link)
        row = convert_map_to_table_row(map)
        texts[normalize(name)] = row

    table = []
    filename_src = os.path.join(os.path.dirname(__file__), 'taro_empty.csv')
    with open(filename_src, 'r') as f:
        reader = csv.reader(f, delimiter=';')
        for i, line in enumerate(reader):
            card_name = (line[1] + ' ' + line[2]).strip()
            card_texts = texts[normalize(card_name)]
            table.append(line[:3] + card_texts)

    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    filename_dest = os.path.join(os.path.dirname(__file__), 'taro-' + timestamp + '.csv')
    with open(filename_dest, 'w') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerows(table)


if __name__ == '__main__':
    main()
