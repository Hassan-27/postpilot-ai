from __future__ import annotations
import uuid
from sqlalchemy import DateTime, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base, TimestampMixin


class Schedule(Base, TimestampMixin):
    __tablename__ = "schedules"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    post_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("posts.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,           # one schedule per post
        index=True,
    )
    scheduled_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,            # Celery beat queries this constantly
    )
    is_processed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationship
    post: Mapped["Post"] = relationship("Post", back_populates="schedule")

    def __repr__(self) -> str:
        return f"<Schedule post={self.post_id} at={self.scheduled_at}>"