import re

from libs.triggers.event_type import TriggerName


def get_topic_name(trigger_name: TriggerName) -> str:
    # Convert camel case to underscore separated string
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1-\2", trigger_name.value)
    topic_name = re.sub("([a-z0-9])([A-Z])", r"\1-\2", s1).upper()
    return topic_name
