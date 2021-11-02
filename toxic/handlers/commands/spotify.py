import telegram

from toxic.features.music.spotify import Spotify
from toxic.handlers.handler import CallbackHandler
from toxic.messenger.messenger import Messenger
from toxic.repositories.settings import SettingsRepository


class SpotifyEnqueueCallback(CallbackHandler):
    def __init__(self, settings_repo: SettingsRepository, messenger: Messenger, spotify: Spotify):
        self.settings_repo = settings_repo
        self.messenger = messenger
        self.spotify = spotify

    @staticmethod
    def is_admins_only() -> bool:
        return True

    def handle(self, callback: telegram.CallbackQuery, message: telegram.Message, args: dict):
        if not self.settings_repo.is_spotify_enabled():
            self.messenger.reply_callback(callback, 'Spotify выключен.', show_alert=True)
            return

        device_id = self.settings_repo.spotify_get_device()
        if device_id is None:
            self.messenger.reply_callback(callback, 'Нужно сначала выбрать устройство.', show_alert=True)
            return

        uri = args.get('url')
        if uri is None:
            # TODO: log
            return

        self.spotify.add_to_queue(uri, device_id)
