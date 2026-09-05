import asyncio
import uuid
import app.db.init_db  # noqa: F401
from app.workers.celery_app import celery_app
from app.core.logging import get_logger

logger = get_logger(__name__)


async def _publish_post(post_id: str):
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
    from app.models.post import Post, PostStatus
    from app.models.post_log import PostLog
    from app.services.discord_service import publish_to_discord
    from sqlalchemy import select
    from app.core.config import get_settings

    settings = get_settings()
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    try:
        async with session_factory() as db:
            # Fetch the post
            result = await db.execute(
                select(Post).where(Post.id == uuid.UUID(post_id))
            )
            post = result.scalar_one_or_none()

            if not post:
                logger.error(f"Post {post_id} not found")
                return

            # Publish to Discord
            success = await publish_to_discord(post.content)

            if success:
                post.status = PostStatus.PUBLISHED
                log = PostLog(
                    post_id=post.id,
                    event="published",
                    detail="Published to Discord successfully",
                )
            else:
                post.status = PostStatus.FAILED
                log = PostLog(
                    post_id=post.id,
                    event="failed",
                    detail="Discord webhook failed",
                )

            db.add(log)
            await db.commit()
            logger.info(f"Post {post_id} status updated to {post.status}")

    finally:
        await engine.dispose()

@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    name="tasks.publish_post",
)
def publish_post_task(self, post_id: str):
    try:
        logger.info(f"Starting publish task for post {post_id}")
        asyncio.run(_publish_post(post_id))
        logger.info(f"Post {post_id} published successfully")
    except Exception as exc:
        logger.error(f"Failed to publish post {post_id}: {exc}")
        raise self.retry(exc=exc)


async def _check_and_enqueue_due_posts():
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
    from app.services.scheduler_service import get_due_posts, mark_schedule_processed
    from app.core.config import get_settings

    settings = get_settings()
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    try:
        async with session_factory() as db:
            due_schedules = await get_due_posts(db)

            if not due_schedules:
                logger.info("No posts due for publishing")
                return

            logger.info(f"Found {len(due_schedules)} post(s) due for publishing")

            for schedule in due_schedules:
                publish_post_task.delay(str(schedule.post_id))
                await mark_schedule_processed(db, schedule.id)

            await db.commit()
            logger.info(f"Enqueued {len(due_schedules)} publish task(s)")
    finally:
        await engine.dispose()


@celery_app.task(name="tasks.check_scheduled_posts")
def check_scheduled_posts():
    logger.info("Checking for scheduled posts due for publishing...")
    asyncio.run(_check_and_enqueue_due_posts())


@celery_app.task(name="tasks.test_task")
def test_task(message: str):
    logger.info(f"Test task received: {message}")
    return f"Processed: {message}"