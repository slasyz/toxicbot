import gzip
import logging
from typing import Union

import psycopg2
import telegram
import yaml

from src import db


def handle_user(cur: psycopg2._psycopg.cursor, user: telegram.User):
    cur.execute('''
        SELECT first_name, last_name, username 
        FROM users 
        WHERE tg_id=%s
    ''', (user.id,))
    res = cur.fetchone()

    if res is None:
        cur.execute('''
            INSERT INTO users(tg_id, first_name, last_name, username)
            VALUES(%s, %s, %s, %s)
        ''', (
            user.id,
            user.first_name,
            user.last_name,
            user.username
        ))
    elif res[0] != user.first_name or res[1] != user.last_name != user.username:
        cur.execute('''
            UPDATE users
            SET first_name = %s,
                last_name = %s,
                username = %s
            WHERE tg_id = %s
        ''', (
            user.first_name,
            user.last_name,
            user.username,
            user.id
        ))


def handle_chat(cur: psycopg2._psycopg.cursor, chat: telegram.Chat):
    cur.execute('SELECT title FROM chats WHERE tg_id=%s', (chat.id,))

    res = cur.fetchone()
    if res is None:
        cur.execute('''
            INSERT INTO chats(tg_id, title)
            VALUES(%s, %s)
        ''', (
            chat.id,
            chat.title
        ))
    elif res[0] != chat.title:
        cur.execute('''
            UPDATE chats
            SET title = %s
            WHERE tg_id=%s
        ''', (
            chat.title,
            chat.id
        ))


def handle_message(message: telegram.Message, update_id: Union[int, type(None)] = None):
    with db.conn, db.conn.cursor() as cur:
        if message.from_user is not None:
            handle_user(cur, message.from_user)
        if message.chat is not None:
            handle_chat(cur, message.chat)

        cur.execute('SELECT true FROM messages WHERE chat_id=%s AND tg_id=%s AND update_id=%s',
                    (
                        message.chat_id,
                        message.message_id,
                        update_id
                    ))
        if cur.fetchone() is not None:
            return

        cur.execute('''
            INSERT INTO messages(chat_id, tg_id, user_id, update_id, text, date)
            VALUES(%s, %s, %s, %s, %s, %s)
        ''', (
            message.chat_id,
            message.message_id,
            message.from_user.id,
            update_id,
            message.text,
            message.date,
        ))


def handle(update: telegram.Update):
    with db.conn, db.conn.cursor() as cur:
        cur.execute('SELECT true FROM updates WHERE tg_id=%s', (update.update_id,))
        if cur.fetchone() is not None:
            logging.info(f'ignoring {update.update_id}')
            return

        print(update)

        message = update.message or update.edited_message
        chat_id = 0
        if message is not None:
            chat_id = message.chat_id

        dump = yaml.dump(update).encode('utf-8')
        dump = gzip.compress(dump)

        cur.execute('''
            INSERT INTO updates(tg_id, chat_id, dump)
            VALUES(%s, %s, %s)
        ''', (
            update.update_id,
            chat_id,
            dump
        ))

    if message is None:
        return

    handle_message(message, update.update_id)
