from enum import Enum
from typing import Optional

from pydantic import BaseModel


class EntityType(str, Enum):
    Mellishops = "mellishops"
    Vtex = "vtex"


class TriggerName(str, Enum):
    Mellishops = "Mellishops"
    Vtex = "Vtex"


# Chamar de Events ao inves de Trigger
class Trigger(BaseModel):
    trigger_name: TriggerName
    id: Optional[str]
    entity_id: str
    entity_type: EntityType
