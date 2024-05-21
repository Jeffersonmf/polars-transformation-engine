import json

from libs.triggers.event_type import EntityType
from libs.triggers.mellishops import Mellishops
from libs.triggers.vtex import Vtex


class TriggersValidator(object):
    """
    Description
    ----------
    Class responsible for validating the schemas and data structures
    consumed from the Broker.

    Schemas inherit from the BaseEntityTypes superclass, organized by
    specific topics linked to each Entity Type.
    """

    def __init__(self):
        self.invalid_trigger_type = "Incorrect Trigger Type"
        self.valid_entities = EntityType

    def __extract_event__(self, event_message):
        self.event_key = str(event_message.get("key"))
        self.topic_name = str(event_message.get("topic_name")).lower()
        self.event_message = event_message
        self.trigger_name = json.loads(event_message.get("value"))[
            "trigger_name"
        ]  # mudar para CONNECTOR NAME

    def __instance_of_triggername__(self, trigger_object):
        try:
            trigger_decoded = trigger_object.parse_raw(
                self.event_message["value"].decode()
            )

            if (
                trigger_decoded.entity_type is None
                or len(trigger_decoded.entity_type) <= 0
            ):
                raise Exception(
                    {
                        "entity_type_dlq": f"{self.trigger_name}:{self.event_key}",
                        "error": "The Entity Type is not defined",
                    }
                )

        except Exception as e:
            raise Exception(e)
        finally:
            return trigger_decoded

    def validate_message(self, event_message):
        if event_message is None:
            return None

        self.__extract_event__(event_message=event_message)

        if self.trigger_name is not None:
            trigger_type = getattr(
                self, self.trigger_name, lambda: self.invalid_trigger_type
            )()
            return (
                (True, trigger_type)
                if trigger_type is not self.invalid_trigger_type
                else (False, None)
            )
        else:
            return (False, None)

    def Mellishops(self):
        return self.__instance_of_triggername__(Mellishops)

    def Vtex(self):
        return self.__instance_of_triggername__(Vtex)

    def default(self):
        return "Incorrect Entity Type"

    switcher = {
        1: Mellishops,
        2: Vtex,
        18: default,
    }
