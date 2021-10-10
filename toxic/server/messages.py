import logging

from fastapi import APIRouter
from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates

from toxic.db import Database
from toxic.server.models import UserMessage, User, GroupMessage, Group


def get_router(templates: Jinja2Templates, database: Database) -> APIRouter:
    router = APIRouter(
        prefix='/messages',
        responses={404: {'description': 'Not found'}},
    )

    @router.get('/', response_class=HTMLResponse)
    async def chats(request: Request):
        logging.info('открываем чятики')

        groups_dict = {}
        users_dict = {}

        # Получаем чаты
        rows = database.query('''
            SELECT c.tg_id, c.title, count(m)
            FROM chats c
                LEFT JOIN messages m ON c.tg_id = m.chat_id
            WHERE c.tg_id < 0
            GROUP BY c.tg_id, c.title
            ORDER BY c.title
        ''')
        for row in rows:
            groups_dict[row[0]] = Group(row[0], row[1], row[2])

        # Получаем пользователей
        rows = database.query('''
            SELECT u.tg_id, btrim(concat(u.first_name, ' ', u.last_name)) as name, count(m)
            FROM users u
                LEFT JOIN messages m on u.tg_id = m.chat_id
            GROUP BY u.tg_id, u.first_name, u.last_name
            ORDER BY name
        ''')
        for row in rows:
            users_dict[row[0]] = User(row[0], row[1], row[2])

        groups_list = []
        for val in groups_dict.values():
            groups_list.append(val)
        users_list = []
        for val in users_dict.values():
            users_list.append(val)

        return templates.TemplateResponse('chats.html', {
            'request': request,
            'groups': groups_list,
            'users': users_list,
        })

    @router.get('/group/{id}', response_class=HTMLResponse)
    async def group(request: Request, id: int):
        # Получаем чат
        row = database.query_row('''
            SELECT c.title, count(m)
            FROM chats c
                LEFT JOIN messages m ON c.tg_id = m.chat_id
            WHERE c.tg_id = %s
            GROUP BY c.tg_id, c.title
        ''', (id,))
        group = Group(id, row[0], row[1])

        messages = []

        # Получаем все сообщения из чата
        rows = database.query('''
            SELECT update_id, m.tg_id, user_id, btrim(concat(u.first_name, ' ', u.last_name)), date, text
            FROM messages m
                JOIN users u ON m.user_id = u.tg_id
            WHERE chat_id = %s
            ORDER BY tg_id NULLS FIRST, json_id, update_id
        ''', (id,))
        for row in rows:
            update_id, tg_id, user_id, user_name, date, text = row

            if not text:
                text = ''

            date = date.astimezone(tz=None)

            message = GroupMessage(update_id, tg_id, user_id, user_name, date, text)
            messages.append(message)

        return templates.TemplateResponse('group.html', {
            'request': request,
            'group': group,
            'messages': messages,
        })

    @router.get('/user/{id}', response_class=HTMLResponse)
    async def user(request: Request, id: int):
        # Получаем пользователя
        row = database.query_row('''
            SELECT btrim(concat(u.first_name, ' ', u.last_name)), count(m)
            FROM users u
                LEFT JOIN messages m ON u.tg_id = m.chat_id 
            WHERE u.tg_id = %s
            GROUP BY u.tg_id, u.first_name, u.last_name
        ''', (id,))
        user = User(id, row[0], row[1])

        messages = []

        # Получаем все сообщения от пользователя
        rows = database.query('''
            SELECT chat_id, update_id, tg_id, date, text
            FROM messages m
            WHERE chat_id = %s
            ORDER BY tg_id NULLS FIRST, json_id, update_id
        ''', (id,))
        for row in rows:
            user_id, update_id, tg_id, date, text = row

            if not text:
                text = ''

            date = date.astimezone(tz=None)

            message = UserMessage(update_id, tg_id, user_id, date, text)
            messages.append(message)

        return templates.TemplateResponse('user.html', {
            'request': request,
            'user': user,
            'messages': messages,
        })

    return router
