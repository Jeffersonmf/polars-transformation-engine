from typing import Optional

import traitlets
from decouple import config as env_config

from libs.configurations.config_base import ConfigBase

# loaded config
config_kafka = {
    "brokers": env_config("KAFKA_BROKERS", default="localhost:9092"),
    "port": env_config("KAFKA_PORT", default=9092),
    "db": env_config("KAFKA_TOPICS", default="mellishops"),
    "partitions": env_config("KAFKA_PARTITIONS", default="1"),
    "replicas": env_config("KAFKA_REPLICAS", default="1"),
    "group.id": env_config("ENV", default="dev"),
    "dlq.name": env_config("DLQ_TOPIC_NAME", default="DLQ"),
    "enable.auto.commit": env_config("ENABLE_AUTO_COMMIT", default=False),
    "auto.offset.reset": env_config("AUTO_OFFSET_RESET", default="latest"),
}


class KafkaConfig(ConfigBase):
    """
    Specialized class to provide centralized environment
    settings control of Kafka Broker.
    """

    def __init__(self) -> None:
        super().__init__(self.get_default_config())

    def get_brokers(self) -> Optional[traitlets.traitlets.Any]:
        return super()._get_property("brokers")

    def get_default_config(self):
        return config_kafka

    def get_group_id(self):
        return super()._get_property("group.id")

    def get_dlq_topic_name(self):
        return super()._get_property("dlq.name")

    def get_kafka_properties(self):
        return {
            # "security.protocol": "PLAINTEXT",
            "enable.auto.commit": super()._get_property("enable.auto.commit"),
            "auto.offset.reset": super()._get_property("auto.offset.reset"),
        }
