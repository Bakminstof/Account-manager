from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base
from database.tps import str_300, str_1000

if TYPE_CHECKING:
    from apps.accounts.db.models import Account


class User(Base):
    __tablename__ = "user"

    repr_cols = ("id", "username")

    username: Mapped[str_300]
    email: Mapped[str_300 | None]
    hashed_password: Mapped[str_1000]
    is_active: Mapped[bool] = mapped_column(default=True)
    is_superuser: Mapped[bool] = mapped_column(default=False)
    is_verified: Mapped[bool] = mapped_column(default=False)

    # =============================|Accounts relationship|============================== #
    accounts: Mapped[list[Account]] = relationship(back_populates="user")

    # ===================================|Table args|=================================== #
    __table_args__ = (
        Index(f"ix__{__tablename__}__username", "username", unique=True),
        UniqueConstraint("username", name=f"{__tablename__}__username_uc"),
        UniqueConstraint("email", name=f"{__tablename__}__email_uc"),
    )
