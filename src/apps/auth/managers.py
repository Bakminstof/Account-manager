from re import match
from string import ascii_lowercase, ascii_uppercase, digits, punctuation

from bcrypt import checkpw, gensalt, hashpw
from fastapi import status
from sqlalchemy import or_

from apps.auth.db.models import User
from apps.auth.db.orm import UserDatabase
from apps.auth.db.utils import get_user_db
from apps.auth.schemas import UserCreateModel, UserLoginModel
from core.settings import settings
from exceptions import AuthenticationError, ValidationError


class PasswordHelper:
    password_min_length = settings.auth.password_min_length

    lowercase_letters_min_count = settings.auth.password_lowercase_letters_min_count
    uppercase_letters_min_count = settings.auth.password_uppercase_letters_min_count
    digits_min_count = settings.auth.password_digits_min_count
    spec_symbols_min_count = settings.auth.password_spec_symbols_min_count

    def validate_created_password(self, user_dict: dict[str, str | None]) -> bool:
        password = user_dict["password"]
        password_check = user_dict.pop("password_check")

        password_length = len(password)

        if password_length < self.password_min_length:
            raise ValidationError("Пароль слишком короткий", locations=["password"])

        if password != password_check:
            raise ValidationError(
                "Пароли не совпадают",
                locations=["password_check"],
            )

        lowercase_letters_count = 0
        uppercase_letters_count = 0
        digits_count = 0
        spec_symbols_count = 0

        for letter in password:
            if letter in ascii_lowercase:
                lowercase_letters_count += 1
            elif letter in ascii_uppercase:
                uppercase_letters_count += 1
            elif letter in digits:
                digits_count += 1
            elif letter in punctuation:
                spec_symbols_count += 1
            else:
                ValueError(f"Unwanted character: `{letter}`")

            if (
                (lowercase_letters_count >= self.lowercase_letters_min_count)
                and (uppercase_letters_count >= self.uppercase_letters_min_count)
                and (digits_count >= self.digits_min_count)
                and (spec_symbols_count >= self.spec_symbols_min_count)
            ):
                return True

        raise ValidationError(
            "Пароль не соответствует требованиям",
            locations=["password"],
        )

    def hash(self, password: str) -> bytes:
        return hashpw(
            password=password.encode(encoding=settings.base_encoding),
            salt=gensalt(),
        )

    def validate(self, password: str, hashed_password: bytes) -> bool:
        if not password:
            return False

        return checkpw(
            password=password.encode(encoding=settings.base_encoding),
            hashed_password=hashed_password,
        )


class UserManager:
    password_helper = PasswordHelper()

    # def __init__(self) -> None:
    #     self.

    async def get_by_id(self, user_id: int) -> User | None:
        async with get_user_db() as user_db:  # type: UserDatabase
            return await user_db.get_by_id(user_id)

    async def get_by_username(self, username: str) -> User | None:
        async with get_user_db() as user_db:  # type: UserDatabase
            return await user_db.get_by_username(username)

    async def get_by_email(self, user_email: str) -> User | None:
        async with get_user_db() as user_db:  # type: UserDatabase
            return await user_db.get_by_email(user_email)

    async def validate_username(self, user_create: UserCreateModel) -> None:
        username_pattern = r"^\S+$"

        if not match(username_pattern, user_create.username):
            raise ValidationError("Неверный формат логина", locations=["username"])

        if await self.get_by_username(user_create.username) is not None:
            raise ValidationError(
                "Пользователь с таким логином уже существует",
                locations=["username"],
            )

    async def validate_email(
        self,
        user_create: UserCreateModel,
        can_empty: bool = False,
    ) -> None:
        if user_create.email:
            email_pattern = r"^\S+@\S+\.\S+$"

            if not match(email_pattern, user_create.email):
                raise ValidationError("Неверный формат почты", locations=["email"])

            if await self.get_by_email(user_create.email) is not None:
                raise ValidationError(
                    "Почта уже используется",
                    locations=["email"],
                )

        elif not can_empty:
            raise ValidationError(
                "Обязательное поле",
                locations=["email"],
            )

    async def create(
        self,
        user_create: UserCreateModel,
        validate_password: bool = True,
    ) -> User:
        await self.validate_username(user_create)
        await self.validate_email(user_create, can_empty=True)

        user_dict = user_create.model_dump()

        if validate_password:
            self.password_helper.validate_created_password(
                user_dict,
            )

        password = user_dict.pop("password")
        user_dict["hashed_password"] = self.password_helper.hash(password)

        async with get_user_db() as user_db:  # type: UserDatabase
            created_user = (await user_db.create([user_dict]))[0]

        await self.on_after_register(created_user)

        return created_user

    @classmethod
    async def validate_auth_user(cls, user_login: UserLoginModel) -> User:
        async with get_user_db() as user_db:  # type: UserDatabase
            where = [
                or_(
                    User.username == user_login.username,
                    User.email == user_login.username,
                ),
            ]

            user = await user_db.get(where)

        if not user:
            raise ValidationError(
                "Неверный логин или пароль", locations=["username", "password"]
            )

        if not cls.password_helper.validate(user_login.password, user.hashed_password):
            raise ValidationError(
                "Неверный логин или пароль", locations=["username", "password"]
            )

        if not user.is_active:
            raise AuthenticationError(
                "Пользователь заблокирован",
                status_code=status.HTTP_403_FORBIDDEN,
                locations=["username"],
            )

        return user

    # =====================================|Hooks|====================================== #
    async def on_after_register(self, user: User) -> None:
        pass

    async def on_after_update(self, user: User) -> None:
        pass

    async def on_after_request_verify(self, user: User) -> None:
        pass

    async def on_after_verify(self, user: User) -> None:
        pass

    async def on_after_forgot_password(self, user: User) -> None:
        pass

    async def on_after_reset_password(self, user: User) -> None:
        pass

    async def on_after_login(self, user: User) -> None:
        pass

    async def on_before_delete(self, user: User) -> None:
        pass

    async def on_after_delete(self, user: User) -> None:
        pass
