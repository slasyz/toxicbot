import json
from typing import Optional

from toxic.db import Database


class SettingsRepository:
    def __init__(self, database: Database):
        self.database = database

    def _set_value(self, key: str, value: Optional[str]):
        if value is None:
            self.database.exec('DELETE FROM settings WHERE key=%s', (key,))
            return

        self.database.exec('''
            INSERT INTO settings(key, value) 
            VALUES(%s, %s) 
            ON CONFLICT(key) DO UPDATE
                SET value = %s 
        ''', (key, value, value))

    def _get_value(self, key: str) -> Optional[str]:
        row = self.database.query_row('SELECT value FROM settings WHERE key=%s', (key,))
        if row is None:
            return None

        return row[0]

    def spotify_set_device(self, device_id: str):
        self._set_value('spotify_device_id', device_id)

    def spotify_enable(self):
        self._set_value('spotify_enabled', 'yes')

    def spotify_disable(self):
        self._set_value('spotify_enabled', None)

    def is_spotify_enabled(self) -> bool:
        return self._get_value('spotify_enabled') is not None

    def spotify_get_device(self) -> Optional[str]:
        return self._get_value('spotify_device_id')

    def spotify_get_token(self) -> Optional[dict]:
        value_str = self._get_value('spotify_token')
        if value_str is None:
            return None

        return json.loads(value_str)

    def spotify_set_token(self, token_info: dict):
        value_str = json.dumps(token_info)
        return self._set_value('spotify_token', value_str)
