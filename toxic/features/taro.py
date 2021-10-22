from __future__ import annotations

import csv
import os
import random
from dataclasses import dataclass
from typing import Tuple


@dataclass
class Row:
    name: str = ''
    general_forwards: str = ''
    general_backwards: str = ''
    love_forwards: str = ''
    love_backwards: str = ''
    question_forwards: str = ''
    question_backwards: str = ''
    daily: str = ''
    advice: str = ''


def convert_table_row(name: str, row: list) -> Row:
    return Row(
        name=name,
        general_forwards=row[0],
        general_backwards=row[1],
        love_forwards=row[2],
        love_backwards=row[3],
        question_forwards=row[4],
        question_backwards=row[5],
        daily=row[6],
        advice=row[7],
    )


class Taro:
    """
    This was made only to laugh at this, obviously I don't believe in that.
    """
    def __init__(self, res_dir: str, csv_table: dict[str, Row]):
        self.res_dir = res_dir
        self.csv_table = csv_table

    @staticmethod
    def new(res_dir) -> Taro:
        table = {}

        filename_src = os.path.join(res_dir, 'taro.csv')
        with open(filename_src, 'r') as f:
            reader = csv.reader(f, delimiter=';')
            for line in reader:
                card_name = (line[1] + ' ' + line[2]).strip()
                table[line[0]] = convert_table_row(card_name, line[3:11])

        return Taro(res_dir, table)

    def get_random_card(self) -> Tuple[Row, bytes]:  # TODO: do not do that
        files = os.listdir(os.path.join(self.res_dir, 'taro_cards'))
        card = random.choice(files)
        with open(os.path.join(self.res_dir, 'taro_cards', card), 'rb') as f:
            image = f.read()

        return self.csv_table[card], image
