from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import DateTime, func


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


# Import all models here so Alembic can find them
from app.models.user import User          # noqa: F401, E402
from app.models.post import Post          # noqa: F401, E402
from app.models.schedule import Schedule  # noqa: F401, E402
from app.models.post_log import PostLog   # noqa: F401, E402