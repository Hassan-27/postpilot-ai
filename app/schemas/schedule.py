from pydantic import BaseModel, field_validator
from datetime import datetime, timezone
import uuid


class ScheduleCreate(BaseModel):
    scheduled_at: datetime

    @field_validator("scheduled_at")
    @classmethod
    def must_be_future(cls, v: datetime) -> datetime:
        if v <= datetime.now(timezone.utc):
            raise ValueError("Scheduled time must be in the future")
        return v


class ScheduleResponse(BaseModel):
    id: uuid.UUID
    post_id: uuid.UUID
    scheduled_at: datetime
    is_processed: bool

    model_config = {"from_attributes": True}