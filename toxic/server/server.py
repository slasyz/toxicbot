import os
from asyncio import CancelledError

import uvicorn
from fastapi import FastAPI
from starlette_exporter import PrometheusMiddleware, handle_metrics
from starlette.templating import Jinja2Templates

from main import init, init_sentry
from toxic.server import messages


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
    config, database, _, _, _ = init(
        [os.path.join(os.path.dirname(__file__), '..', '..', 'config.json'), '/etc/toxic/config.json']
    )

    init_sentry(config)

    app = FastAPI()
    app.add_middleware(PrometheusMiddleware)

    templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), '..', '..', 'html'))

    routes = [
        messages.get_router(templates, database),
    ]

    for route in routes:
        app.include_router(route)

    app.add_route("/metrics", handle_metrics)

    try:
        uvicorn.run(app, host=config['server']['host'], port=config['server']['port'], log_config=LOGGING_CONFIG)
    except CancelledError:
        pass


if __name__ == '__main__':
    __main__()
