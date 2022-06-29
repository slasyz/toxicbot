import _thread
import asyncio
import traceback
from datetime import datetime

import asyncpg
from loguru import logger

from toxic.messenger.messenger import Messenger

MAX_ERRORS_PER_MINUTE = 3


class Worker:
    async def work(self):
        raise NotImplementedError()


class WorkerWrapper:
    def __init__(self, worker: Worker, messenger: Messenger):
        self.worker = worker
        self.messenger = messenger
        self.counter: set[datetime] = set()

    def _clean_counter(self):
        now = datetime.now()
        self.counter = {x for x in self.counter if (now - x).total_seconds() <= 60}

    async def run(self):
        while True:
            try:
                await self.worker.work()
                return
            except Exception as ex:
                traceback.print_stack()
                logger.opt(exception=ex).error('Exception in worker %s.', self.__class__.__name__)

                self._clean_counter()
                self.counter.add(datetime.now())
                if len(self.counter) >= MAX_ERRORS_PER_MINUTE:
                    logger.opt(exception=ex).error(
                        'Got %d errors in worker %s in last minute, stopping.',
                        len(self.counter), self.__class__.__name__,
                    )
                    try:
                        await self.messenger.send_to_admins(f'Воркер {type(self.worker).__name__} бросил исключение {len(self.counter)} раз. Выход.')
                    except AttributeError:
                        # Скорее всего, ошибка возникла на старте, когда ещё нет подключения к телеге.
                        # Если бот не запустится, это будет заметно сразу.
                        pass
                    except asyncpg.InterfaceError:
                        # Ошибка БД, не получилось отправить сообщение.
                        pass

                    _thread.interrupt_main()
                    return


class WorkersManager:
    def __init__(self, messenger: Messenger):
        self.messenger = messenger

    async def run(self, workers: list[Worker]):
        tasks = []
        for worker in workers:
            wrapper = WorkerWrapper(worker, self.messenger)
            t = asyncio.create_task(wrapper.run())
            tasks.append(t)

        await asyncio.gather(*tasks)
