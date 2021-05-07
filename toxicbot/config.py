# TODO: everything in this file is very very bad.

import json
from dataclasses import dataclass

c = {}


def load(filepath):
    with open(filepath) as f:
        global c
        c = json.load(f)


@dataclass
class DB:
    host: str
    port: int
    database: str
    user: str
    password: str


def get_database_creds() -> DB:
    database = c['database']['database']
    if isinstance(database, dict):
        with open(database['file']) as f:
            database = f.read()
    user = c['database']['user']
    if isinstance(user, dict):
        with open(user['file']) as f:
            user = f.read()
    password = c['database']['password']
    if isinstance(password, dict):
        with open(password['file']) as f:
            password = f.read()

    return DB(c['database']['host'], c['database']['port'], database, user, password)


def get_telegram_token() -> str:
    token = c['telegram']['token']
    if isinstance(token, str):
        return token

    with open(token['file']) as f:
        return f.read()


def get_server_port() -> int:
    return c['server']['port']
