from json import dumps
from logging import getLogger
from typing import Any, Callable, Coroutine

from fastapi import FastAPI, HTTPException, status
from fastapi.exceptions import RequestValidationError, ValidationException
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from starlette.responses import RedirectResponse
from starlette.templating import _TemplateResponse

from core.ctx_proc import render_template
from core.settings import settings

from .exceptions import APIError, AuthenticationError, NotFoundError, ValidationError

logger = getLogger(__name__)


def create_exception_handler[
    E: (
        type(APIError),
        type(AuthenticationError),
        type(NotFoundError),
        type(ValidationError),
    )
](create_func=None, assignable_type: E | None = None) -> Callable[
    [Request, APIError], Coroutine[Any, Any, JSONResponse]
]:
    def make_log(request: Request, error_data: dict) -> None:
        message = f"URL:=`{request.url}`, user=`{request.user}`, exception=`{dumps(error_data)}`"
        logger.warning(message)

    async def exception_handler(
        request: Request,
        exception: E | HTTPException,
    ) -> JSONResponse:
        if assignable_type:
            exc = assignable_type(
                detail=exception.detail,
                status_code=exception.status_code,
                headers=exception.headers,
            )
        elif create_func:
            exc = create_func(request, exception)
        else:
            exc = exception

        error_data = {"error_type": exc.__class__.__name__, "error_message": exc.detail}

        if exc.locations:
            error_data["error_locations"] = exc.locations

        make_log(request, error_data)

        return JSONResponse(
            content=error_data,
            status_code=exc.status_code,
            headers=exc.headers,
        )

    return exception_handler


def create_validation_error(
    request: Request,
    exception: RequestValidationError | ValidationException | ValidationError,
) -> ValidationError:
    def create_validation_error_data(
        exception: RequestValidationError | ValidationException,
    ) -> dict[str, str | list]:
        exc_mess_list = []

        for exc in exception.errors():
            exc_mess_list.append(f"{exc['msg']}. Request location: {exc['loc']}")

        return {"messages": exc_mess_list}

    error_data = create_validation_error_data(exception)

    if isinstance(exception, RequestValidationError):
        body = f". Body: {exception.body}"
    else:
        body = None

    exc_mess = f"{' |\n'.join(error_data['messages'])}{body if body else ""}"

    return ValidationError(detail=exc_mess)


async def not_found_handler(
    request: Request,
    exception: NotFoundError,
) -> _TemplateResponse:
    return render_template(
        "not-found.html",
        request,
        status_code=status.HTTP_404_NOT_FOUND,
    )


def login_redirect_handler(
    request: Request,
    exception: AuthenticationError,
):
    return RedirectResponse(url=settings.login_url, status_code=status.HTTP_302_FOUND)


def register_exc_handlers(app: FastAPI) -> None:
    # ======================================|400|======================================= #
    app.add_exception_handler(
        exc_class_or_status_code=status.HTTP_400_BAD_REQUEST,
        handler=create_exception_handler(assignable_type=APIError),
    )
    # ======================================|401|======================================= #
    app.add_exception_handler(
        exc_class_or_status_code=status.HTTP_401_UNAUTHORIZED,
        handler=login_redirect_handler,
    )
    # ======================================|403|======================================= #
    app.add_exception_handler(
        exc_class_or_status_code=status.HTTP_403_FORBIDDEN,
        handler=create_exception_handler(assignable_type=AuthenticationError),
    )
    # ======================================|404|======================================= #
    app.add_exception_handler(
        exc_class_or_status_code=status.HTTP_404_NOT_FOUND,
        handler=not_found_handler,
    )
    # ======================================|405|======================================= #
    app.add_exception_handler(
        exc_class_or_status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
        handler=create_exception_handler(assignable_type=APIError),
    )
    # ======================================|422|======================================= #
    app.add_exception_handler(
        exc_class_or_status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        handler=create_exception_handler(),
    )
    app.add_exception_handler(
        exc_class_or_status_code=RequestValidationError,
        handler=create_exception_handler(create_func=create_validation_error),
    )
    app.add_exception_handler(
        exc_class_or_status_code=ValidationException,
        handler=create_exception_handler(create_func=create_validation_error),
    )
    # ======================================|500|======================================= #
    app.add_exception_handler(
        exc_class_or_status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        handler=create_exception_handler(assignable_type=APIError),
    )
