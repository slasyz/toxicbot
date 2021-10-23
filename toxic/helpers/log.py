import logging
import sys
from datetime import datetime

import sentry_sdk
from loguru import logger
from sentry_sdk.integrations.logging import BreadcrumbHandler, EventHandler, LoggingIntegration


def interval(seconds: float) -> str:
    days, remainder = divmod(seconds, 24*60*60)
    hours, remainder = divmod(remainder, 60*60)
    minutes, seconds = divmod(remainder, 60)

    return '{:.0f}d {:.0f}h {:.0f}m {:.2f}s'.format(days, hours, minutes, seconds)


def print_sleep(seconds: float, until: str):
    f = interval(seconds)
    logger.info('Sleeping {} until {}.', f, until)


class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__ or frame.f_code.co_filename == sentry_sdk.integrations.logging.__file__:
            frame = frame.f_back
            depth += 1

        # traceback.print_tb()
        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def init_sentry(dsn: str):
    if dsn:
        logger.add(
            BreadcrumbHandler(level=logging.DEBUG),
            level=logging.DEBUG,
        )

        logger.add(
            EventHandler(level=logging.ERROR),
            format='{message}',
            level=logging.ERROR,
        )

        integrations = [
            LoggingIntegration(level=None, event_level=None),
        ]

        sentry_sdk.init(dsn, integrations=integrations)  # pylint: disable=abstract-class-instantiated


def init():
    logger.remove()
    logger.level('DEBUG', color='<yellow>')
    logger.level('INFO', color='<blue>')
    logger.level('ERROR', color='<red><bold>')
    logger.add(
        sys.stderr,
        format='| {time:YYYY-MM-DD HH:mm:ssZZ} {name} {level} | <level>{message}</level> | {extra}',  # pylint: disable=W1401
        colorize=True,
        level='INFO',
    )

    print('\n****************** ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' ******************\n')
    logging.basicConfig(handlers=[InterceptHandler()], level=0)
