from enum import StrEnum
from typing import Sequence

from fastapi.requests import Request

from apps.accounts.db.models import Account
from apps.accounts.db.orm import AccountDatabase
from apps.accounts.db.utils import get_acc_db
from apps.accounts.schemas import AccountCreateModel, AccountUpdateModel
from apps.auth.db.models import User


async def search_account_by_name(
    user: User,
    name: str | None = None,
    details: str | None = None,
    is_active: bool = True,
    exact_match: bool = False,
) -> list[Account]:
    if name == "*":
        name = ""

    results = []

    async with get_acc_db() as acc_db:  # type: AccountDatabase
        load_options = {
            "user_id": user.id,
            "name": name,
            "details": details,
            "is_active": is_active,
            "exact_match": exact_match,
            "order_by": Account.name,
        }

        async for accounts in acc_db.aiter_load(
            acc_db.search_by_name_or_details,
            **load_options,
        ):  # type: Sequence[Account]

            results.extend(accounts)

    return results


async def search_accounts_by_ids(
    user: User,
    accounts_ids: list[int] | tuple[int] | None = None,
    is_active: bool = True,
) -> list[Account]:
    results = []

    async with get_acc_db() as acc_db:  # type: AccountDatabase
        load_options = {
            "user_id": user.id,
            "accounts_ids": accounts_ids,
            "is_active": is_active,
        }

        async for accounts in acc_db.aiter_load(
            acc_db.search_by_id,
            **load_options,
        ):  # type: Sequence[Account]
            results.extend(accounts)

    return results


async def create_accounts(accounts: list[Account]) -> None:
    async with get_acc_db() as acc_db:  # type: AccountDatabase
        await acc_db.create(accounts)


async def create_new_account(user_id: int, account_create: AccountCreateModel) -> None:
    async with get_acc_db() as acc_db:  # type: AccountDatabase
        create_account_dict = {"user_id": user_id, **account_create.model_dump()}

        await acc_db.create([create_account_dict])


async def update_account(user_id: int, account_update: AccountUpdateModel) -> None:
    async with get_acc_db() as acc_db:  # type: AccountDatabase
        update_dict = {"user_id": user_id, **account_update.model_dump()}

        await acc_db.update([update_dict])


class SupportedEncodings(StrEnum):
    utf_8: str = "UTF-8"
    win_1251: str = "windows-1251"


def get_encoding_by_user_agent(request: Request) -> str:
    user_agent = request.headers.get("user-agent")

    if not user_agent:
        return SupportedEncodings.utf_8

    user_agent = user_agent.lower()

    if "win" in user_agent or "windows" in user_agent:
        encoding = SupportedEncodings.win_1251

    elif "linux" in user_agent:
        encoding = SupportedEncodings.utf_8

    else:
        encoding = SupportedEncodings.utf_8

    return encoding
