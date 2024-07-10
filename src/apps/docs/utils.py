from json import dumps
from typing import Sequence

from fastapi.openapi.utils import get_openapi
from fastapi.routing import BaseRoute

from core.settings import settings


def make_openapi_json(
    title: str,
    version: str,
    routes: Sequence[BaseRoute],
    filename: str = "openapi.json",
    encoding: str = settings.base_encoding,
) -> None:
    openapi_schema = get_openapi(title=title, version=version, routes=routes)
    openapi_path = settings.static.static_dir / filename

    with openapi_path.open(mode="w", encoding=encoding) as file:
        file.write(dumps(openapi_schema))
