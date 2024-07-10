from contextlib import AbstractAsyncContextManager, asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession

from apps.accounts.db.orm import AccountDatabase
from database.utils import get_async_session


@asynccontextmanager
async def get_acc_db() -> AbstractAsyncContextManager[AccountDatabase]:
    async with get_async_session() as async_session:  # type: AsyncSession
        yield AccountDatabase(async_session)
