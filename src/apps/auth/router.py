from fastapi import APIRouter, Depends, status
from fastapi.requests import Request
from fastapi.security import APIKeyCookie
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.templating import _TemplateResponse

from apps.auth.db.models import User
from apps.auth.managers import UserManager
from apps.auth.schemas import UserCheckModel, UserCheckStatusModel, UserCreateModel
from apps.auth.utils import create_home_logged_redirect, login_require
from core.ctx_proc import render_template
from core.settings import settings
from exceptions import AuthenticationError, ValidationError

app_name = "auth"
router = APIRouter()

cookie = APIKeyCookie(name=settings.auth.cookie_key, auto_error=False)


# ======================================|Register|====================================== #
@router.get(
    path=settings.register_url,
    response_class=HTMLResponse,
    status_code=status.HTTP_200_OK,
)
async def register_form(request: Request) -> _TemplateResponse:
    if request.user:
        return create_home_logged_redirect()

    context = {
        "PASSWORD_MIN_LENGTH": settings.auth.password_min_length,
        "PASSWORD_LOWERCASE_LETTERS_MIN_COUNT": settings.auth.password_lowercase_letters_min_count,
        "PASSWORD_UPPERCASE_LETTERS_MIN_COUNT": settings.auth.password_uppercase_letters_min_count,
        "PASSWORD_DIGITS_MIN_COUNT": settings.auth.password_digits_min_count,
        "PASSWORD_SPEC_SYMBOLS_MIN_COUNT": settings.auth.password_spec_symbols_min_count,
    }

    return render_template(f"{app_name}/register-form.html", request, context)


@router.post(
    path=settings.register_url,
    status_code=status.HTTP_302_FOUND,
    response_class=RedirectResponse,
)
async def register(request: Request, user: UserCreateModel):
    if request.user:
        raise AuthenticationError(
            detail="User already registered",
            status_code=status.HTTP_403_FORBIDDEN,
        )

    user_manager = UserManager()
    created_user = await user_manager.create(user)

    return create_home_logged_redirect(created_user)


# =======================================|Login|======================================== #
@router.get(
    path=settings.login_url,
    response_class=HTMLResponse,
    status_code=status.HTTP_200_OK,
)
async def login_form(request: Request):
    if not request.user:
        return render_template(f"{app_name}/login-form.html", request)

    return create_home_logged_redirect()


@router.post(
    path=settings.login_url,
    status_code=status.HTTP_302_FOUND,
    response_class=RedirectResponse,
)
async def login(
    request: Request,
    user: User = Depends(UserManager.validate_auth_user),
):
    if request.user:
        raise AuthenticationError(
            detail="User already logged",
            status_code=status.HTTP_403_FORBIDDEN,
        )

    return create_home_logged_redirect(user)


# =======================================|Logout|======================================= #
@router.post(
    path=settings.logout_url,
    status_code=status.HTTP_302_FOUND,
    response_class=RedirectResponse,
)
async def logout(request: Request):
    if not request.user:
        raise AuthenticationError(
            detail="Not found authorized users",
            status_code=status.HTTP_403_FORBIDDEN,
        )

    redirect = RedirectResponse(
        url=settings.home_url,
        status_code=status.HTTP_302_FOUND,
    )

    redirect.delete_cookie(key=settings.auth.cookie_key)

    return redirect


# =======================================|Check|======================================== #
@router.post("/check", response_model=UserCheckModel, status_code=status.HTTP_200_OK)
async def check_username(usercheck: UserCheckModel):
    if not usercheck.username and not usercheck.email:
        raise ValidationError(
            f"One of {list(UserCheckModel.model_fields.keys())} must be",
            locations=["username", "email"],
        )

    user_manager = UserManager()

    if usercheck.username:
        usercheck.username = (
            UserCheckStatusModel.exists
            if await user_manager.get_by_username(usercheck.username)
            else UserCheckStatusModel.free
        )

    if usercheck.email:
        usercheck.email = (
            UserCheckStatusModel.exists
            if await user_manager.get_by_email(usercheck.email)
            else UserCheckStatusModel.free
        )

    return usercheck
