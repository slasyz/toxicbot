-- TODO: add NOT NULL constraints.

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";  -- Run as superuser

CREATE TABLE users (
    tg_id       bigint PRIMARY KEY,
    first_name  text,
    last_name   text,
    username    text,
    admin       bool DEFAULT FALSE
);

-- INSERT INTO users(tg_id, first_name, admin)
-- VALUES (59352582, 'Вячеслав', TRUE);

CREATE TABLE chats (
    tg_id          bigint PRIMARY KEY,
    title          text,
    chain_period   int  DEFAULT 30,
    joke_period    int  DEFAULT 7
);

CREATE TABLE updates (
    tg_id   bigint PRIMARY KEY,
    chat_id bigint,
    created timestamptz DEFAULT now(),
    json    jsonb       DEFAULT NULL
);

CREATE TABLE messages (
    chat_id   bigint REFERENCES chats(tg_id),
    tg_id     bigint,
    json_id   bigint DEFAULT NULL,
    user_id   bigint REFERENCES users(tg_id),
    update_id bigint REFERENCES updates(tg_id),

    text      text,
    date      timestamptz,
    sticker   text
);
CREATE UNIQUE INDEX ON messages(chat_id, json_id, tg_id);
CREATE UNIQUE INDEX ON messages(chat_id, json_id) WHERE tg_id IS NULL;

CREATE TABLE reminders (
    id       serial4     PRIMARY KEY,
    chat_id  bigint      REFERENCES chats(tg_id),
    datetime timestamptz NOT NULL,
    text     text        NOT NULL,
    isactive bool        NOT NULL
);
CREATE INDEX ON reminders(datetime);

CREATE TABLE settings (
    id    serial4 PRIMARY KEY,
    key   text    NOT NULL UNIQUE,
    value text
);

CREATE TABLE callback_data (
    id    serial4 PRIMARY KEY,
    value jsonb   UNIQUE
);
