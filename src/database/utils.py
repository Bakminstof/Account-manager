from contextlib import AbstractAsyncContextManager, asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession

from database.helper import AsyncDatabase
from database.mixins import AuditMixin
from database.triggers import on_update_trigger

db = AsyncDatabase()


@asynccontextmanager
async def get_async_session() -> AbstractAsyncContextManager[AsyncSession]:
    async with db.session() as async_session:  # type: AsyncSession
        yield async_session


async def set_triggers() -> None:
    async with get_async_session() as async_session:  # type: AsyncSession
        audit_tables = [d.__tablename__ for d in AuditMixin.__subclasses__()]  # type: ignore

        for table in audit_tables:
            await async_session.execute(on_update_trigger(table))

        await async_session.commit()
