import sys
import logging
from datetime import datetime


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
