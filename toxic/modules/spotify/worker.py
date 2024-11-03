from asyncio.queues import Queue

from toxic.repository import Repository


class SpotifyCacheWorker:
    """
    This class saves token to database, see spotify.Cache documentation for details.
    """

    def __init__(self, repo: Repository):
        self.repo = repo
        self.queue: Queue = Queue(maxsize=-1)

    def put(self, token: dict):
        self.queue.put_nowait(token)

    async def work(self):
        while True:
            token = await self.queue.get()
            if not isinstance(token, dict):
                continue
            await self.repo.spotify_token_set(token)
