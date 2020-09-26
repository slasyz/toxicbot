import _thread
import logging
import threading
import traceback
from datetime import datetime
from typing import List

from src.helpers import general

MAX_ERRORS_PER_MINUTE = 3


class Worker:
    def __init__(self):
        self.counter = set()

    def _clean_counter(self):
        now = datetime.now()
        is_last_min = lambda x: (now - x).total_seconds() <= 60
        self.counter = set([x for x in self.counter if is_last_min(x)])

    def work(self):
        raise Exception('method work() must be implemented')

    def start(self):
        while True:
            try:
                self.work()
            except Exception as e:
                traceback.print_stack()
                print(e)

                self._clean_counter()
                self.counter.add(datetime.now())
                if len(self.counter) >= MAX_ERRORS_PER_MINUTE:
                    logging.error(f'{len(self.counter)} errors in worker {self.__class__.__name__} in last minute, stopping')
                    try:
                        general.send_to_admins(f'Воркер {self.__class__.__name__} бросил исключение {len(self.counter)} раз. Выход.')
                    except AttributeError:
                        # Скорее всего, ошибка возникла на старте, когда ещё нет подключения к телеге.
                        # Если бот не запустится, это будет заметно сразу.
                        pass

                    _thread.interrupt_main()
                    return


def start_workers(workers: List[Worker]):
    for worker in workers:
        thread = threading.Thread(target=worker.start)
        thread.start()
