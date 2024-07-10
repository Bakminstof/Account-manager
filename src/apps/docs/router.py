from fastapi import APIRouter
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.responses import HTMLResponse

from core.settings import settings

app_name = "docs"
router = APIRouter()


@router.get("/redoc", include_in_schema=False)
async def redoc_html() -> HTMLResponse:
    return get_redoc_html(
        openapi_url=settings.docs.openapi_url,
        title=f"{settings.api_name} - ReDoc",
        redoc_js_url=f"{settings.static.url}/{settings.static.js_dir.name}/{app_name}/redoc.standalone.js",
        redoc_favicon_url=f"{settings.static.url}/{settings.static.media_dir.name}/{app_name}/docs_favicon.png",
    )


@router.get("/docs", include_in_schema=False)
async def swagger_ui_html() -> HTMLResponse:
    return get_swagger_ui_html(
        openapi_url=settings.docs.openapi_url,
        title=f"{settings.api_name} - Swagger UI",
        oauth2_redirect_url=settings.docs.swagger_ui_oauth2_redirect_url,
        swagger_js_url=f"{settings.static.url}/{settings.static.js_dir.name}/{app_name}/swagger-ui-bundle.js",
        swagger_css_url=f"{settings.static.url}/{settings.static.css_dir.name}/{app_name}/swagger-ui.css",
        swagger_favicon_url=f"{settings.static.url}/{settings.static.media_dir.name}/{app_name}/docs_favicon.png",
    )


@router.get(settings.docs.swagger_ui_oauth2_redirect_url, include_in_schema=False)
async def swagger_ui_redirect() -> HTMLResponse:
    return get_swagger_ui_oauth2_redirect_html()
