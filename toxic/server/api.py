from fastapi import APIRouter
from starlette.requests import Request
from starlette.responses import JSONResponse


def get_router() -> APIRouter:
    router = APIRouter(
        prefix='/api',
        responses={404: {'description': 'Not found'}},
    )

    @router.get('/test', response_class=JSONResponse)
    async def test_get(request: Request):
        return JSONResponse({
            'result': 'ok',
        })

    @router.post('/test', response_class=JSONResponse)
    async def test_post(request: Request):
        has_payload = len(await request.body()) > 0
        return JSONResponse({
            'result': 'ok',
            'payload': (await request.json()) if has_payload else None,
        })

    return router
