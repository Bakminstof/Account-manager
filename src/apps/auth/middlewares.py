from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from apps.auth.db.utils import get_user_db
from apps.auth.utils import decode_jwt
from core.settings import settings


class AuthJWTCookieMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        access_key: str | None = request.cookies.get(settings.auth.cookie_key)

        if not access_key:
            request.scope["user"] = None

            return await call_next(request)

        payload = decode_jwt(access_key)
        username = payload.get("sub")

        if not username:
            request.scope["user"] = None

            return await call_next(request)

        async with get_user_db() as user_db:
            user = await user_db.get_by_username(username)

            request.scope["user"] = user

        return await call_next(request)
