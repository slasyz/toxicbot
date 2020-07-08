CREATE TABLE users (
    tg_id       int4 PRIMARY KEY,
    first_name  text,
    last_name   text,
    username    text,
    admin       bool DEFAULT FALSE
);

-- INSERT INTO users(tg_id, first_name, admin)
-- VALUES (59352582, 'Вячеслав', TRUE);

CREATE TABLE chats (
    tg_id int4 PRIMARY KEY,
    title text
);

CREATE TABLE updates (
    tg_id   int4 PRIMARY KEY,
    chat_id int4,
    created timestamptz DEFAULT now(),
    dump    bytea
);

CREATE TABLE messages (
    chat_id   int4 REFERENCES chats(tg_id),
    tg_id     int4,
    user_id   int4 REFERENCES users(tg_id),
    update_id int4 REFERENCES updates(tg_id),

    text      text,
    date      timestamptz,

    PRIMARY KEY (chat_id, tg_id)
);
