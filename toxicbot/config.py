import json


def load(files: list[str]):
    for file in files:
        try:
            with open(file) as f:
                return json.load(f)
        except FileNotFoundError:
            pass

    raise Exception('cannot load config')
