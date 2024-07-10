from logging import getLogger
from logging.config import dictConfig
from pathlib import Path
from warnings import warn

from core.settings import settings

logger = getLogger(__name__)


def setup_logging() -> None:
    dictConfig(settings.logging.dict_config)

    if settings.debug:
        msg = "Debug mode on"
        logger.warning(msg)
        warn(UserWarning(msg))

    else:
        if settings.logging.sentry:
            import sentry_sdk  # type: ignore

            sentry_sdk.init(settings.logging.sentry, traces_sample_rate=1)
