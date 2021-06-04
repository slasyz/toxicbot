import json
from typing import Union


class Config:
    def __init__(self, data: dict):
        self.data = data

    def __getitem__(self, item):
        return self.data[item]


class ConfigFactory:
    @staticmethod
    def load_secret(src: Union[dict, str]) -> str:
        if isinstance(src, str):
            return src

        with open(src['file']) as f:
            return f.read()

    def load(self, files: list[str]) -> Config:
        for file in files:
            try:
                with open(file) as f:
                    data = json.load(f)
            except FileNotFoundError:
                continue

            return Config(data)

        raise Exception('cannot load config: no files found')
