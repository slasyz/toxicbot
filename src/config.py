import json

c = {}


def load(filepath):
    with open(filepath) as f:
        global c #, bot_id
        c = json.load(f)

        #bot_id = int(config['telegram']['token'].split(':')[0])
