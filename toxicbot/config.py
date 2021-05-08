import json
from typing import Union


def load_secret(src: Union[dict, str]) -> str:
    if isinstance(src, str):
        return src

    with open(src['file']) as f:
        return f.read()


def load_secrets(data: dict):
    # TODO: do it better.
    data['database']['name'] = load_secret(data['database']['name'])
    data['database']['user'] = load_secret(data['database']['user'])
    data['database']['pass'] = load_secret(data['database']['pass'])
    data['telegram']['token'] = load_secret(data['telegram']['token'])


def load(files: list[str]):
    for file in files:
        try:
            with open(file) as f:
                data = json.load(f)
                load_secrets(data)
                return data
        except FileNotFoundError:
            pass

    raise Exception('cannot load config')
