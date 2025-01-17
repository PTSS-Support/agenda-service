import logging

import uvicorn
from fastapi import FastAPI
from fastapi.logger import logger
from prometheus_fastapi_instrumentator import Instrumentator
from starlette.responses import RedirectResponse

from src.auth.configuration import configure_security_scheme
from src.auth.middleware import AuthenticationMiddleware
from src.controllers.agenda_controller import agenda_router
from src.exceptions.configuration import configure_exception_handlers
from src.manage.router import router as health_router
from src.settings import settings


app = FastAPI(
    title=settings.SERVICE_TITLE,
    description=settings.SERVICE_DESCRIPTION,
    version=settings.SERVICE_VERSION,
)

configure_exception_handlers(app)

Instrumentator().instrument(app).expose(
    app=app,
    endpoint="/manage/prometheus",
    include_in_schema=False
)

@app.get(
    path="/",
    include_in_schema=False
)
async def root():
    return RedirectResponse("/docs", status_code=302)



app.add_middleware(AuthenticationMiddleware)

app.include_router(health_router)
app.include_router(agenda_router)

configure_security_scheme(app, settings.ACCESS_TOKEN_COOKIE_NAME)

if __name__ == "__main__":
    logger.setLevel(logging.DEBUG)

    config = uvicorn.Config(
        app,
        host=settings.HOST,
        port=settings.PORT,
        use_colors=True,
        log_level=settings.LOG_LEVEL,
    )

    server = uvicorn.Server(config)
    server.run()
