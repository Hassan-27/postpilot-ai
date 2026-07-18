import asyncio
from app.workers.celery_app import celery_app
from app.core.logging import get_logger

logger = get_logger(__name__)


def run_async(coro):
    """Helper to run async functions inside sync Celery tasks."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(name="tasks.test_task")
def test_task(message: str):
    """Simple task to verify Celery is working."""
    logger.info(f"Test task received: {message}")
    return f"Processed: {message}"


@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    name="tasks.publish_post",
)
def publish_post_task(self, post_id: str):
    """Background task to publish a post. Full implementation in Step 10."""
    try:
        logger.info(f"Starting publish task for post {post_id}")
        run_async(_publish_post(post_id))
        logger.info(f"Post {post_id} published successfully")
    except Exception as exc:
        logger.error(f"Failed to publish post {post_id}: {exc}")
        raise self.retry(exc=exc)


async def _publish_post(post_id: str):
    from app.db.session import AsyncSessionLocal
    from app.models.post import Post, PostStatus
    from sqlalchemy import select
    import uuid

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Post).where(Post.id == uuid.UUID(post_id))
        )
        post = result.scalar_one_or_none()

        if not post:
            logger.error(f"Post {post_id} not found")
            return

        post.status = PostStatus.PUBLISHED
        await db.commit()
        logger.info(f"Post {post_id} marked as published")