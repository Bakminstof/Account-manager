from fastapi import FastAPI

from apps.accounts import accounts_router
from apps.auth import auth_router
from apps.docs import docs_router


def register_routers(app: FastAPI) -> None:
    app.include_router(
        docs_router,
        tags=["Docs"],
    )
    app.include_router(
        auth_router,
        tags=["Auth"],
    )
    app.include_router(
        accounts_router,
        tags=["Accounts"],
    )
