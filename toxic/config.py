from __future__ import annotations

import json


class Config:
    def __init__(self, data: dict):
        self.data = data

    @staticmethod
    def load(files: list[str]) -> Config:
        for file in files:
            try:
                with open(file) as f:
                    data = json.load(f)
            except FileNotFoundError:
                continue

            return Config(data)

        raise Exception('Cannot load config: no files found.')

    def __getitem__(self, item):
        return self.data[item]
