from __future__ import annotations
import uuid
import enum
from sqlalchemy import String, Text, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base, TimestampMixin
from app.models.schedule import Schedule
from app.models.user import User


class PostStatus(str, enum.Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    FAILED = "failed"


class Post(Base, TimestampMixin):
    __tablename__ = "posts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[PostStatus] = mapped_column(
        Enum(PostStatus),
        default=PostStatus.DRAFT,
        nullable=False,
        index=True,
    )
    ai_generated: Mapped[bool] = mapped_column(default=False, nullable=False)
    linkedin_post_id: Mapped[str] = mapped_column(String(100), nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="posts")
    schedule: Mapped["Schedule"] = relationship("Schedule", back_populates="post", uselist=False)
    logs: Mapped[list["PostLog"]] = relationship("PostLog", back_populates="post")

    def __repr__(self) -> str:
        return f"<Post {self.id} [{self.status}]>"