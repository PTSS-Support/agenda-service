import logging

import uvicorn
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from starlette.responses import RedirectResponse

from src.auth.configuration import configure_security_scheme
from src.auth.middleware import AuthenticationMiddleware
from src.controllers.agenda_controller import agenda_router
from src.exceptions.exception_handler import configure_exception_handlers
from src.manage.router import router as health_router
from src.settings import settings


def configure_logging():
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logging.getLogger("uvicorn.error").setLevel(logging.CRITICAL)
    # Keep other loggers as they are
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger(__name__).setLevel(logging.DEBUG)

# Add this before creating the FastAPI app
configure_logging()

app = FastAPI(
    title=settings.SERVICE_TITLE,
    description=settings.SERVICE_DESCRIPTION,
    version=settings.SERVICE_VERSION,
)

app.add_middleware(AuthenticationMiddleware)

Instrumentator().instrument(app).expose(
    app=app,
    endpoint="/metrics",
    include_in_schema=False
)

@app.get(
    path="/",
    include_in_schema=False
)
async def root():
    return RedirectResponse("/docs", status_code=302)



configure_exception_handlers(app)

app.include_router(health_router)
app.include_router(agenda_router)

configure_security_scheme(app, settings.ACCESS_TOKEN_COOKIE_NAME)

if __name__ == "__main__":
    config = uvicorn.Config(
        app,
        host=settings.HOST,
        port=settings.PORT,
        use_colors=True,
        log_level=settings.LOG_LEVEL,
    )

    server = uvicorn.Server(config)
    server.run()
