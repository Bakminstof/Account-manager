from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from apps.accounts.schemas import AccountStatus
from database.base import Base
from database.tps import json_col, str_100

if TYPE_CHECKING:
    from apps.auth.db.models import User


class Account(Base):
    __tablename__ = "account"
    repr_cols = ("id", "name", "data")

    name: Mapped[str_100]
    data: Mapped[json_col]
    status: Mapped[AccountStatus] = mapped_column(default=AccountStatus.active)

    # ===============================|User relationship|================================ #
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    user: Mapped[User] = relationship(back_populates="accounts")
    # ===================================|Table args|=================================== #
    __table_args__ = (Index(f"ix__{__tablename__}__name", "name"),)
