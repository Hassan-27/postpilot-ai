import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.schedule import Schedule
from app.models.post import Post, PostStatus
from app.core.logging import get_logger

logger = get_logger(__name__)


async def schedule_post(
    db: AsyncSession,
    post_id: uuid.UUID,
    user_id: uuid.UUID,
    scheduled_at: datetime,
) -> Schedule:
    # Verify post exists and belongs to user
    result = await db.execute(
        select(Post).where(Post.id == post_id, Post.user_id == user_id)
    )
    post = result.scalar_one_or_none()

    if not post:
        raise ValueError("Post not found")

    if post.status != PostStatus.DRAFT:
        raise ValueError("Only draft posts can be scheduled")

    if scheduled_at <= datetime.now(timezone.utc):
        raise ValueError("Scheduled time must be in the future")

    # Check if already scheduled
    existing = await db.execute(
        select(Schedule).where(Schedule.post_id == post_id)
    )
    if existing.scalar_one_or_none():
        raise ValueError("Post is already scheduled")

    # Create schedule
    schedule = Schedule(
        post_id=post_id,
        scheduled_at=scheduled_at,
    )
    db.add(schedule)

    # Update post status
    post.status = PostStatus.SCHEDULED
    await db.flush()
    await db.refresh(schedule)

    logger.info(f"Post {post_id} scheduled for {scheduled_at}")
    return schedule


async def get_due_posts(db: AsyncSession) -> list[Schedule]:
    """Fetch all schedules that are due and not yet processed."""
    now = datetime.now(timezone.utc)
    result = await db.execute(
        select(Schedule)
        .where(
            Schedule.scheduled_at <= now,
            Schedule.is_processed == False,  # noqa: E712
        )
    )
    return list(result.scalars().all())


async def mark_schedule_processed(db: AsyncSession, schedule_id: uuid.UUID) -> None:
    result = await db.execute(
        select(Schedule).where(Schedule.id == schedule_id)
    )
    schedule = result.scalar_one_or_none()
    if schedule:
        schedule.is_processed = True
        await db.flush()