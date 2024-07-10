from enum import StrEnum, auto

from pydantic import BaseModel, ConfigDict


class UserReadModel(BaseModel):
    id: int
    username: str
    email: str | None = None
    hashed_password: bytes | None = None
    is_active: bool | None = None
    is_superuser: bool | None = None
    is_verified: bool | None = None


class UserCreateModel(BaseModel):
    username: str
    password: str
    password_check: str
    email: str | None = None


class UserUpdateModel(BaseModel):
    password: str | None = None
    email: str | None = None
    is_active: bool | None = None
    is_superuser: bool | None = None
    is_verified: bool | None = None


class TokenInfo(BaseModel):
    token: str
    type: str


class UserCheckStatusModel(StrEnum):
    exists: str = auto()
    free: str = auto()


class UserCheckModel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    username: str | None | UserCheckStatusModel = None
    email: str | None | UserCheckStatusModel = None


class UserLoginModel(BaseModel):
    username: str | None = None
    password: str | None = None
