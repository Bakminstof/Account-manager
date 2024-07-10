from contextlib import AbstractAsyncContextManager, asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession

from apps.auth.db.orm import UserDatabase
from database.utils import get_async_session


@asynccontextmanager
async def get_user_db() -> AbstractAsyncContextManager[UserDatabase]:
    async with get_async_session() as async_session:  # type: AsyncSession
        yield UserDatabase(async_session)
