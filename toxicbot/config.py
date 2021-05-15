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

    def load_secrets(self, data: dict):
        # TODO: do it better.
        data['database']['name'] = self.load_secret(data['database']['name'])
        data['database']['user'] = self.load_secret(data['database']['user'])
        data['database']['pass'] = self.load_secret(data['database']['pass'])
        data['telegram']['token'] = self.load_secret(data['telegram']['token'])

    def load(self, files: list[str]) -> Config:
        for file in files:
            try:
                with open(file) as f:
                    data = json.load(f)
                    self.load_secrets(data)
                    return Config(data)
            except FileNotFoundError:
                pass

        raise Exception('cannot load config: no files found')
