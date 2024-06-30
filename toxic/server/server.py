import os
import time
from asyncio import CancelledError

import uvicorn
from fastapi import FastAPI
from starlette_exporter import PrometheusMiddleware, handle_metrics
from starlette.templating import Jinja2Templates

from main import init_with_config, get_resource_path
from toxic.config import Config
from toxic.helpers import log
from toxic.helpers.log import init_sentry
from toxic.server import messages, api

LOGGING_CONFIG: dict = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {},
    "handlers": {},
    "loggers": {
        "uvicorn": {"handlers": [], "level": "INFO"},
        "uvicorn.error": {"level": "INFO"},
        "uvicorn.access": {"handlers": [], "level": "INFO"},
    },
}


def __main__():
    log.init()
    os.environ['TZ'] = 'Europe/Moscow'
    time.tzset()  # pylint: disable=no-member

    config_files = [os.path.join(os.path.dirname(__file__), '..', '..', 'config.json'), '/etc/toxic/config.json']
    config = Config.load(config_files)

    app = FastAPI()
    app.add_middleware(PrometheusMiddleware)

    async def server_init():
        deps = await init_with_config(config)
        init_sentry(deps.config['sentry']['dsn'])

        html_dir = get_resource_path('html')
        templates = Jinja2Templates(directory=html_dir)

        routes = [
            messages.get_router(templates, deps.database),
            api.get_router(),
        ]

        for route in routes:
            app.include_router(route)

        app.add_route("/metrics", handle_metrics)

    app.add_event_handler('startup', server_init)

    try:
        uvicorn.run(
            app,
            host=config['server']['host'],
            port=config['server']['port'],
            log_config=LOGGING_CONFIG,
        )
    except CancelledError:
        pass


if __name__ == '__main__':
    __main__()
