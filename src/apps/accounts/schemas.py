from enum import StrEnum, auto

from pydantic import BaseModel, ConfigDict


class AccountStatus(StrEnum):
    active = auto()
    deleted = auto()


class AccountCreateModel(BaseModel):
    model_config = ConfigDict(strict=True)

    name: str
    data: dict


class AccountUpdateModel(AccountCreateModel):
    id: int


class ExportType(StrEnum):
    json = auto()
    txt = auto()


class ExportModel(BaseModel):
    accounts_ids: list[int] | tuple[int]
    export_type: ExportType = ExportType.txt
