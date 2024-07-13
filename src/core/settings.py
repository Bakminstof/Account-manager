from enum import StrEnum, auto
from functools import cached_property
from os import environ
from pathlib import Path

from pydantic import BaseModel, ConfigDict, computed_field, field_validator
from pydantic_core.core_schema import ValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL
from starlette.templating import Jinja2Templates

from log.settings import LoggingSettings

BASE_DIR = Path(__file__).parent.parent
ENV_DIR = BASE_DIR / "env"
CERTS_DIR = BASE_DIR.parent / "certs"

environ.setdefault(
    "ENV_FILE",
    (ENV_DIR / "dev.env").absolute().as_posix(),
)


def get_abs_path(root: Path, value: str) -> Path:
    if len(value) < 1:
        raise ValueError("Path must be defined")

    path = Path(value)

    if value.startswith("/") or value[1:3] == ":\\":
        directory = path
    else:
        directory = root / value

    return directory


class StaticSettings(BaseModel):
    url: str = "/static"

    static_dir: Path | str = "static"

    js_dir: Path | str = "js"
    css_dir: Path | str = "css"
    media_dir: Path | str = "media"
    fonts_dir: Path | str = "fonts"

    @field_validator("static_dir")
    def static_dir_validator(
        cls,
        value: str,
        info: ValidationInfo,
        **kwargs,
    ) -> Path:
        return get_abs_path(BASE_DIR.parent, value)

    @field_validator(
        "js_dir",
        "css_dir",
        "media_dir",
        "fonts_dir",
    )
    def dirs_validator(
        cls,
        value: str,
        info: ValidationInfo,
        **kwargs,
    ) -> Path:
        return get_abs_path(info.data["static_dir"], value)


class DocsSettings(BaseModel):
    openapi_url: str = "/openapi.json"
    swagger_ui_oauth2_redirect_url: str = "/docs/oauth2-redirect"


class DBSettings(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    drivername: str

    user: str | None = None
    password: str | None = None

    host: str | None = None
    port: int | str | None = None

    name: str

    echo_sql: bool = False
    echo_pool: bool = False
    max_overflow: int = 10
    pool_size: int = 5

    naming_convention: dict = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_N_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }

    @field_validator("name")
    def db_name_validator(
        cls,
        value: str,
        info: ValidationInfo,
        **kwargs,
    ) -> str:
        if "sqlite" in info.data.get("drivername"):
            return (BASE_DIR.parent / "db" / value).absolute().as_posix()

        return value

    @field_validator(
        "user",
        "password",
        "host",
        "port",
    )
    def db_settings_validator(
        cls,
        value: str | int | None,
        info: ValidationInfo,
        **kwargs,
    ) -> str | int | None:
        if not value:
            if "postgresql" in info.data.get("drivername"):
                raise ValueError(f"`{info.field_name}` must be `set")

            return None

        if info.field_name == "port":
            return int(value)

        return value

    @computed_field
    @cached_property
    def url(self) -> URL:
        return URL.create(
            drivername=self.drivername,
            username=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.name,
        )


class AuthSettings(BaseModel):
    public_key: Path | str = "auth-jwt-public.pem"
    private_key: Path | str = "auth-jwt-private.pem"

    jwt_algorithm: str = "RS512"

    transport: str = "cookie"
    cookie_key: str = "sid"

    access_token_age: int = 7_200  # 2h

    password_min_length: int = 6

    password_lowercase_letters_min_count: int = 1
    password_uppercase_letters_min_count: int = 1
    password_digits_min_count: int = 1
    password_spec_symbols_min_count: int = 1

    @field_validator("certs_dir", mode="before")
    def certs_dir_validator(
        cls,
        value: str,
        info: ValidationInfo,
        **kwargs,
    ) -> Path:
        return get_abs_path(BASE_DIR.parent, value)

    @field_validator("public_key", "private_key")
    def certs_validator(
        cls,
        value: str,
        info: ValidationInfo,
        **kwargs,
    ) -> Path:
        return get_abs_path(CERTS_DIR, value)


class Language(StrEnum):
    eu = auto()
    ru = auto()


class TemplateSettings(BaseModel):
    templates_dir: Path | str = "templates"

    app_name: str = "Менеджер аккаунтов"

    @field_validator("templates_dir")
    def templates_validator(
        cls,
        value: str,
        info: ValidationInfo,
        **kwargs,
    ) -> Jinja2Templates:
        path = get_abs_path(BASE_DIR.parent, value)
        return Jinja2Templates(directory=path.absolute().as_posix())


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="app.",
        env_file=(f"{ENV_DIR / '.env.template'}", environ["ENV_FILE"]),
        case_sensitive=False,
        arbitrary_types_allowed=True,
        env_nested_delimiter=".",
        env_file_encoding="UTF-8",
    )

    # ======================================|Main|====================================== #
    base_encoding: str = "UTF-8"

    api_name: str
    api_version: str

    host: str
    port: int

    base_dir: Path = BASE_DIR
    temp_dir: Path | str = "temp"

    @field_validator("temp_dir")
    def temp_dir_validator(
        cls,
        value: str,
        info: ValidationInfo,
        **kwargs,
    ) -> Path:
        return get_abs_path(BASE_DIR.parent, value)

    public_key: Path | str = "public.pem"
    private_key: Path | str = "private.pem"

    @field_validator("public_key", "private_key")
    def certs_validator(
        cls,
        value: str,
        info: ValidationInfo,
        **kwargs,
    ) -> Path:
        return get_abs_path(CERTS_DIR, value)

    debug: bool = True

    reverse_proxy: bool = True

    origins: list[str]

    lang: Language = Language.ru
    # ====================================|Routing|===================================== #
    home_url: str = "/"

    login_url: str = "/login"
    logout_url: str = "/logout"

    register_url: str = "/register"

    search_url: str = "/search"
    # ====================================|Database|==================================== #
    db: DBSettings
    # =================================|Authentication|================================= #
    auth: AuthSettings
    # ======================================|Docs|====================================== #
    docs: DocsSettings
    # =====================================|Static|===================================== #
    static: StaticSettings
    # ===================================|Templates|==================================== #
    templates: TemplateSettings
    # ====================================|Logging|===================================== #
    logging: LoggingSettings


settings = Settings()
