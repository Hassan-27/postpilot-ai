import httpx
from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


async def publish_to_discord(content: str, username: str = "PostPilot AI") -> bool:
    """
    Publish content to Discord via webhook.
    Returns True on success, False on failure.
    """
    payload = {
        "username": username,
        "content": content,
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.DISCORD_WEBHOOK_URL,
                json=payload,
                timeout=10.0,
            )

        if response.status_code == 204:
            logger.info("Post published to Discord successfully")
            return True
        else:
            logger.error(f"Discord webhook failed: {response.status_code} {response.text}")
            return False

    except httpx.TimeoutException:
        logger.error("Discord webhook timed out")
        return False
    except Exception as e:
        logger.error(f"Discord publish error: {e}")
        return False