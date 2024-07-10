from sqlalchemy import select

from apps.auth.db.models import User
from database.mixins import CRUDMixin


class UserDatabase(CRUDMixin):
    __table__ = User

    async def get(self, where: list | tuple) -> User | None:
        stmt = select(User).where(*where).limit(1)
        result = await self.async_session.scalar(stmt)
        await self.async_session.commit()
        return result

    async def get_by_id(self, user_id: int) -> User | None:
        return await self.get(where=(User.id == user_id,))

    async def get_by_username(self, username: str) -> User | None:
        return await self.get(where=(User.username == username,))

    async def get_by_email(self, user_email: str) -> User | None:
        return await self.get(where=(User.email == user_email,))
