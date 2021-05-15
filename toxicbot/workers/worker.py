import _thread
import logging
import threading
import traceback
from datetime import datetime

import psycopg2

from toxicbot.messenger import Messenger

MAX_ERRORS_PER_MINUTE = 3


class Worker:
    def work(self):
        raise NotImplementedError()


class WorkerWrapper:
    def __init__(self, worker: Worker, messenger: Messenger):
        self.worker = worker
        self.messenger = messenger
        self.counter = set()

    def _clean_counter(self):
        now = datetime.now()
        self.counter = {x for x in self.counter if (now - x).total_seconds() <= 60}

    def run(self):
        while True:
            try:
                self.worker.work()
            except Exception as ex:
                traceback.print_stack()
                print(ex)

                self._clean_counter()
                self.counter.add(datetime.now())
                if len(self.counter) >= MAX_ERRORS_PER_MINUTE:
                    logging.error(
                        'Got %d errors in worker %s in last minute, stopping.',
                        len(self.counter), self.__class__.__name__,
                        exc_info=ex,
                    )
                    try:
                        self.messenger.send_to_admins(f'Воркер {type(self.worker).__name__} бросил исключение {len(self.counter)} раз. Выход.')
                    except AttributeError:
                        # Скорее всего, ошибка возникла на старте, когда ещё нет подключения к телеге.
                        # Если бот не запустится, это будет заметно сразу.
                        pass
                    except psycopg2.InterfaceError:
                        # Ошибка БД, не получилось отправить сообщение.
                        pass

                    _thread.interrupt_main()
                    return


class WorkersManager:
    def __init__(self, messenger: Messenger):
        self.messenger = messenger

    def start(self, workers: list[Worker]):
        for worker in workers:
            wrapper = WorkerWrapper(worker, self.messenger)
            thread = threading.Thread(target=wrapper.run)
            thread.daemon = True
            thread.start()
