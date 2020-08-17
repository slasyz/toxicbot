import sys
import logging
from datetime import datetime


def interval(seconds: float) -> str:
    days, remainder = divmod(seconds, 24*60*60)
    hours, remainder = divmod(remainder, 60*60)
    minutes, seconds = divmod(remainder, 60)

    return '{:.0f}d {:.0f}h {:.0f}m {:.2f}s'.format(days, hours, minutes, seconds)


def print_sleep(seconds: float, until: str):
    f = interval(seconds)
    logging.info(f'sleeping {f} seconds until {until}')


class Logger(object):
    def __init__(self, terminal, logfile):
        self.terminal = terminal
        self.log = logfile

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
        self.log.flush()

    def flush(self):
        self.terminal.flush()
        self.log.flush()


def init():
    logfile = open("log.log", "a")
    sys.stdout = Logger(sys.stdout, logfile)
    sys.stderr = Logger(sys.stderr, logfile)
    print('\n****************** ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' ******************\n')
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
