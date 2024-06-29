from __future__ import annotations

import csv
import os
import random
from dataclasses import dataclass


@dataclass
class CardData:
    filename: str = ''  # e.g. "Swords06.jpg"
    name: str = ''  # e.g. "Шестёрка мечей"
    general_forwards: str = ''
    general_backwards: str = ''
    love_forwards: str = ''
    love_backwards: str = ''
    question_forwards: str = ''
    question_backwards: str = ''
    daily: str = ''
    advice: str = ''


@dataclass
class Card:
    data: CardData
    image: bytes


def convert_table_row(row: list) -> CardData:
    return CardData(
        filename=row[0],
        name=(row[1] + ' ' + row[2]).strip(),
        general_forwards=row[3],
        general_backwards=row[4],
        love_forwards=row[5],
        love_backwards=row[6],
        question_forwards=row[7],
        question_backwards=row[8],
        daily=row[9],
        advice=row[10],
    )


class Taro:
    """
    This was made only to laugh at this, obviously I don't believe in that.
    """

    def __init__(self, res_dir: str, cards_data: list[CardData]):
        self.res_dir = res_dir
        self.cards_data = cards_data

    @staticmethod
    def new(res_dir) -> Taro:
        cards_data = []

        filename_src = os.path.join(res_dir, 'data.csv')
        with open(filename_src, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=';')
            for row in reader:
                data = convert_table_row(row)
                cards_data.append(data)

        return Taro(res_dir, cards_data)

    def get_random_card(self) -> Card:
        data = random.choice(self.cards_data)
        with open(os.path.join(self.res_dir, 'cards', data.filename), 'rb') as f:
            image = f.read()

        return Card(data, image)
