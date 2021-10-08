class Group:
    def __init__(self, id, title, messages):
        self.id = id
        self.title = title
        self.messages = messages


class User:
    def __init__(self, id, name, messages):
        self.id = id
        self.name = name
        self.messages = messages


class GroupMessage:
    def __init__(self, update_id, tg_id, user_id, user_name, date, text):
        self.update_id = update_id
        self.tg_id = tg_id
        self.user_id = user_id
        self.user_name = user_name
        self.date = date
        self.text = text


class UserMessage:
    def __init__(self, update_id, tg_id, user_id, date, text):
        self.update_id = update_id
        self.tg_id = tg_id
        self.user_id = user_id
        self.date = date
        self.text = text
