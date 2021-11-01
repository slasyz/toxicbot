import os

from main import init
from toxic.features.spotify import Spotify
from toxic.repositories.settings import SettingsRepository


def __main__():
    deps = init(
        [os.path.join(os.path.dirname(__file__), '..', 'config.json'), '/etc/toxic/config.json']
    )

    settings_repo = SettingsRepository(deps.database)

    spotify = Spotify.new(deps.config['spotify']['client_id'], deps.config['spotify']['client_secret'], settings_repo)

    if not spotify.is_authenticated():
        print(spotify.get_auth_url())
        redirect_url = input('Enter redirect url: ').strip()
        print(spotify.authenticate(redirect_url))
    else:
        print('Already authenticated.')

    print(spotify.get_devices())


if __name__ == '__main__':
    __main__()
