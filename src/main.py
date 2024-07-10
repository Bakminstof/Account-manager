from fastapi import FastAPI

from core.lifespan import Lifespan
from core.middlewares import register_middlewares
from core.routers import register_routers
from core.settings import settings
from exceptions.handlers import register_exc_handlers

app = FastAPI(
    debug=settings.debug,
    title=settings.api_name,
    version=settings.api_version,
    lifespan=Lifespan().lifespan,
    docs_url=None,
    redoc_url=None,
    swagger_ui_oauth2_redirect_url=None,
    openapi_url=settings.docs.openapi_url,
)

# ====================================|Middlewares|===================================== #
register_middlewares(app)
# ======================================|Routers|======================================= #
register_routers(app)
# =====================================|Exceptions|===================================== #
register_exc_handlers(app)


if __name__ == "__main__":
    if settings.debug:
        import uvicorn

        if settings.reverse_proxy:
            ssl_keyfile = None
            ssl_certfile = None
        else:
            ssl_keyfile = settings.private_key
            ssl_certfile = settings.public_key

        uvicorn.run(
            app="main:app",
            host=settings.host,
            port=settings.port,
            ssl_keyfile=ssl_keyfile,
            ssl_certfile=ssl_certfile,
            reload=True,
        )
