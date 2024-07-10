from sqlalchemy import MetaData, String
from sqlalchemy.orm import DeclarativeBase

from core.settings import settings
from database.mixins import IDPKMixin, ReprMixin
from database.tps import str_100, str_200, str_300, str_1000


class Base(DeclarativeBase, ReprMixin, IDPKMixin):
    __abstract__ = True

    type_annotation_map = {
        str_100: String(100),
        str_200: String(200),
        str_300: String(300),
        str_1000: String(1000),
    }

    metadata = MetaData(naming_convention=settings.db.naming_convention)
