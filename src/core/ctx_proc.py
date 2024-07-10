from fastapi import status
from fastapi.requests import Request
from starlette.templating import _TemplateResponse

from core.settings import settings


def render_template(
    template_name: str,
    request: Request,
    context: dict | None = None,
    status_code: int = status.HTTP_200_OK,
) -> _TemplateResponse:
    base_context = get_base_context()

    if isinstance(context, dict):
        base_context.update(context)

    return settings.templates.templates_dir.TemplateResponse(
        request=request,
        name=template_name,
        context=base_context,
        status_code=status_code,
    )


def get_base_context() -> dict:
    return {
        "APP_NAME": settings.templates.app_name,
        "REGISTER_URL": settings.register_url,
        "SEARCH_URL": settings.search_url,
        "LOGIN_URL": settings.login_url,
        "LOGOUT_URL": settings.logout_url,
    }
