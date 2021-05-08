import _thread
import logging
import threading
import traceback
from datetime import datetime

from toxicbot.helpers import messages

MAX_ERRORS_PER_MINUTE = 3


class Worker:
    def work(self):
        raise NotImplementedError()


class WorkerWrapper:
    def __init__(self, impl: Worker):
        self.counter = set()
        self.impl = impl

    def _clean_counter(self):
        now = datetime.now()
        self.counter = {x for x in self.counter if (now - x).total_seconds() <= 60}

    def start(self):
        while True:
            try:
                self.impl.work()
            except Exception as ex:
                traceback.print_stack()
                print(ex)

                self._clean_counter()
                self.counter.add(datetime.now())
                if len(self.counter) >= MAX_ERRORS_PER_MINUTE:
                    logging.error('%d errors in worker %s in last minute, stopping', len(self.counter), self.__class__.__name__)
                    try:
                        messages.send_to_admins(f'Воркер {self.__class__.__name__} бросил исключение {len(self.counter)} раз. Выход.')
                    except AttributeError:
                        # Скорее всего, ошибка возникла на старте, когда ещё нет подключения к телеге.
                        # Если бот не запустится, это будет заметно сразу.
                        pass

                    _thread.interrupt_main()
                    return


def start_workers(workers: list[Worker]):
    for worker in workers:
        wrapper = WorkerWrapper(worker)
        thread = threading.Thread(target=wrapper.start)
        thread.daemon = True
        thread.start()
