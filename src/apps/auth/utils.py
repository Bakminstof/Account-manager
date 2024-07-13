from datetime import UTC, datetime, timedelta

from jwt import (
    decode,
    encode,
    PyJWTError,
)
from starlette import status
from starlette.requests import Request
from starlette.responses import RedirectResponse

from apps.auth.db.models import User
from core.settings import settings
from exceptions import AuthenticationError


def login_require(request: Request) -> None:
    if not request.user:
        raise AuthenticationError()


def create_home_logged_redirect(
    user: User | None = None,
    create_jwt: bool = True,
    status_code: int = status.HTTP_302_FOUND,
) -> RedirectResponse:
    redirect = RedirectResponse(
        url=settings.home_url,
        status_code=status_code,
    )

    if create_jwt and user:
        jwt_payload = {
            "sub": user.username,
        }

        access_token = encode_jwt(
            payload=jwt_payload,
            token_age=settings.auth.access_token_age,
        )

        redirect.set_cookie(key=settings.auth.cookie_key, value=access_token)

    return redirect


# ========================================|JWT|========================================= #
def encode_jwt(
    payload: dict,
    private_key: str = settings.auth.private_key.read_text(
        encoding=settings.base_encoding,
    ),
    algorithm: str = settings.auth.jwt_algorithm,
    token_age: int = settings.auth.access_token_age,
) -> str:
    now = datetime.now(UTC)

    to_encode = payload.copy()
    to_encode.update(exp=now + timedelta(seconds=token_age), iat=now)

    return encode(payload=to_encode, key=private_key, algorithm=algorithm)


def decode_jwt(
    jwt: bytes | str,
    public_key: str = settings.auth.public_key.read_text(encoding=settings.base_encoding),
    algorithm: str = settings.auth.jwt_algorithm,
) -> dict:
    try:
        payload = decode(jwt=jwt, key=public_key, algorithms=[algorithm])

    except PyJWTError:
        raise {}

    return payload
