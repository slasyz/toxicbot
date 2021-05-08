# TODO: this file is very very bad.

import json

c = {}


def load(filepath):
    with open(filepath) as f:
        global c
        c = json.load(f)
