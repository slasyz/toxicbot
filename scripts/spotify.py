import asyncio
import os

from main import init
from toxic.modules.music.services.spotify import Spotify
from toxic.modules.spotify.worker import SpotifyCacheWorker
from toxic.repository import Repository


async def __main__():
    deps = await init(
        [os.path.join(os.path.dirname(__file__), '..', 'config.json'), '/etc/toxic/config.json']
    )

    repo = Repository(deps.database)
    worker = SpotifyCacheWorker(repo)

    spotify = await Spotify.new(deps.config['spotify']['client_id'], deps.config['spotify']['client_secret'], repo, worker)

    if not spotify.is_authenticated():
        print(spotify.get_auth_url())
        redirect_url = input('Enter redirect url: ').strip()
        print(spotify.authenticate(redirect_url))
    else:
        print('Already authenticated.')

    spotify_searcher = spotify.create_searcher()

    # TODO: move these tests to a bot command

    soad_link = spotify_searcher._get_link_artist('System Of A Down')
    print(soad_link)

    soad_toxicity_link = spotify_searcher._get_link_album('System Of A Down', 'toxicity')
    print(soad_toxicity_link)

    soad_chop_suey_link = spotify_searcher._get_link_song('System Of A Down', 'chop suey')
    print(soad_chop_suey_link)

    scriptonite_link = spotify_searcher._get_link_artist('Скриптонит')
    print(scriptonite_link)


if __name__ == '__main__':
    asyncio.run(__main__())
