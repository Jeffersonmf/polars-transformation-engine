from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from libs.triggers.event_type import EntityType, Trigger


class Vtex(Trigger):
    class Data(BaseModel):
        key: str
        value: str
        id: str
        sensor_id: str
        sample_id: UUID
        sampled_at: datetime

    data: Data
