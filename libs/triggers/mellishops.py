from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from libs.triggers.event_type import Trigger


class Mellishops(Trigger):
    class Data(BaseModel):
        key: str
        value: str

    data: Data
