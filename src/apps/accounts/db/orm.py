from typing import Any

from sqlalchemy import select

from apps.accounts.db.models import Account
from apps.accounts.schemas import AccountStatus
from core.schemas import PaginationResultModel
from database.mixins import PaginationMixin


class AccountDatabase(PaginationMixin):
    __table__ = Account

    @classmethod
    def __build_search_condition(
        cls,
        user_id: int,
        accounts_ids: list[int] | tuple[int] | None = None,
        name: str | None = None,
        details: str | None = None,
        is_active: bool = True,
        exact_match: bool = False,
    ) -> list:
        where = [Account.user_id == user_id]

        if accounts_ids:
            where.append(Account.id.in_(accounts_ids))

        if name:
            if exact_match:
                where.append(Account.name == name)
            else:
                where.append(Account.name.contains(name))

        if details:
            where.append(Account.data.contains(details))

        if is_active:
            where.append(Account.status.is_(AccountStatus.active))

        return where

    async def search_by_name_or_details(
        self,
        user_id: int,
        page: int = 1,
        name: str | None = None,
        details: str | None = None,
        is_active: bool = True,
        exact_match: bool = False,
        limit: int | None = None,
        order_by: Any | None = None,
    ) -> PaginationResultModel:
        where = self.__build_search_condition(
            user_id=user_id,
            name=name,
            details=details,
            is_active=is_active,
            exact_match=exact_match,
        )

        return await self.paginated_result(
            stmt=select(Account).where(*where),
            page=page,
            limit=limit,
            order_by=order_by,
        )

    async def search_by_id(
        self,
        user_id: int,
        accounts_ids: list[int] | tuple[int] | None = None,
        page: int = 1,
        is_active: bool = True,
        limit: int | None = None,
        order_by: Any | None = None,
    ):
        where = self.__build_search_condition(
            user_id=user_id,
            accounts_ids=accounts_ids,
            is_active=is_active,
        )

        return await self.paginated_result(
            stmt=select(Account).where(*where),
            page=page,
            limit=limit,
            order_by=order_by,
        )
