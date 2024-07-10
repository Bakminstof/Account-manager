from contextlib import AbstractAsyncContextManager, asynccontextmanager
from logging import getLogger
from typing import Self

from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

from apps.docs.utils import make_openapi_json
from core.settings import settings
from core.utils import setup_logging
from database.utils import db, set_triggers

logger = getLogger(__name__)


class Lifespan:
    async def on_startup(self, app: FastAPI) -> None:
        setup_logging()

        make_openapi_json(
            settings.api_name,
            settings.api_version,
            app.routes,
        )

        if settings.debug:
            app.mount(
                settings.static.url,
                StaticFiles(directory=settings.static.static_dir),
                name="static",
            )

        await db.init(
            settings.db.url,
            echo_sql=settings.db.echo_sql,
            echo_pool=settings.db.echo_pool,
            max_overflow=settings.db.max_overflow,
            pool_size=settings.db.pool_size,
        )
        await set_triggers()

    async def on_shutdown(self) -> None:
        await db.close()

    @asynccontextmanager
    async def lifespan(self, app: FastAPI) -> AbstractAsyncContextManager[Self]:
        await self.on_startup(app)
        yield
        await self.on_shutdown()

    async def __aenter__(self) -> Self:
        await self.on_startup()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.on_shutdown()
