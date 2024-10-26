from asyncio.queues import Queue

from toxic.repositories.settings import SettingsRepository


class SpotifyCacheWorker:
    """
    This class saves token to database, see spotify.Cache documentation for details.
    """

    def __init__(self, settings_repo: SettingsRepository):
        self.settings_repo = settings_repo
        self.queue: Queue = Queue(maxsize=-1)

    def put(self, token: str):
        self.queue.put_nowait(token)

    async def work(self):
        while True:
            token = await self.queue.get()
            await self.settings_repo.spotify_set_token(token)
