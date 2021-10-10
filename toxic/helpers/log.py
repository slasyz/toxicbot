import logging
from datetime import datetime

import colorama


def interval(seconds: float) -> str:
    days, remainder = divmod(seconds, 24*60*60)
    hours, remainder = divmod(remainder, 60*60)
    minutes, seconds = divmod(remainder, 60)

    return '{:.0f}d {:.0f}h {:.0f}m {:.2f}s'.format(days, hours, minutes, seconds)


def print_sleep(seconds: float, until: str):
    f = interval(seconds)
    logging.info('Sleeping %s until %s', f, until)


def init():
    print('\n****************** ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' ******************\n')
    logging.basicConfig(level=logging.INFO,
                        format=f'-> %(asctime)s - %(name)s - %(levelname)s - {colorama.Fore.BLUE}%(message)s{colorama.Fore.RESET}')
