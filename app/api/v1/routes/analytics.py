import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.dependencies import get_db
from app.api.v1.deps import get_current_user
from app.models.user import User
from app.schemas.analytics import PostLogResponse, AnalyticsSummary
from app.services import analytics_service

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/summary", response_model=AnalyticsSummary)
async def get_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get analytics summary for the current user."""
    summary = await analytics_service.get_analytics_summary(db, current_user.id)
    return summary


@router.get("/posts/{post_id}/logs", response_model=list[PostLogResponse])
async def get_post_logs(
    post_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get the full audit trail for a specific post."""
    try:
        logs = await analytics_service.get_post_logs(db, post_id, current_user.id)
        return logs
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))