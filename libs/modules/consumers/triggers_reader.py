import sys
from asyncio.log import logger

from confluent_kafka import (
    Consumer,
    KafkaError,
    KafkaException,
    Producer,
    TopicPartition,
)

from libs.configurations.kafka_config import KafkaConfig
from libs.modules.events.triggers_handler import TriggersHandler
from libs.modules.validators.trigger_validator import TriggersValidator
from libs.triggers.event_type import TriggerName
from libs.utils.utils import get_topic_name


class TriggersReader(object):
    """
    Description
    ----------
    This module is responsible for consuming the events of the triggers
    in the Broker, creating a whole cache mechanism, managing and controlling
    lock states in [FIFO]-type queues.
    """

    def __init__(self):
        self.state_running = False
        self._conf = KafkaConfig()
        self.__setup_pubsub__()
        self.trigger_name = TriggerName
        self.triggers_handler = TriggersHandler()

    def __load_kafka_properties__(self):
        hosts = {
            "bootstrap.servers": self._conf.get_brokers(),
            "group.id": "data-".join(self._conf.get_group_id()),
        }
        props = self._conf.get_kafka_properties()
        return {**hosts, **props}

    def __setup_pubsub__(self):
        self.producer = Producer(self.__load_kafka_properties__())
        self.consumer = Consumer(self.__load_kafka_properties__())

    def __format_topic_partition__(
        self, topic_name: str, partition: str, offset: str
    ) -> TopicPartition:
        return TopicPartition(topic=topic_name, partition=partition, offset=offset)

    def subscribes_topics(self):
        topic_list: list = []

        for topic in self.trigger_name:
            topic_list.append(get_topic_name(topic))

        self.consumer.subscribe(topic_list)

    def start_all_triggers(self):
        self.subscribes_topics()

        self.state_running = True
        self.__event_polling__()

    def __event_polling__(self) -> None:
        """
        Polling on the kafka stream and
        validate the msg key and value before returning data
        """
        triggers_validator = TriggersValidator()

        try:
            while self.state_running:
                try:
                    # Receiving from Kafka a pure message trigger.
                    msg = self.consumer.poll(timeout=1.0)
                    if msg is None:
                        continue

                    if msg.error():
                        if msg.error().code() == KafkaError._PARTITION_EOF:
                            # End of partition event
                            sys.stderr.write(
                                "%% %s [%d] reached end at offset %d\n"
                                % (msg.topic(), msg.partition(), msg.offset())
                            )
                        elif msg.error():
                            raise KafkaException(msg.error())

                    # TODO: check this treatment after
                    if msg is not None:
                        self.event_message = {
                            "topic_name": str(msg.topic()).upper(),
                            "key": str(msg.key().decode("utf-8")),
                            "value": msg.value(),
                            "offset": msg.offset(),
                            "partition": msg.partition(),
                            "timestamp": msg.timestamp(),
                        }

                        match triggers_validator.validate_message(self.event_message):
                            case (True, trigger_validated):
                                self.handle_message(
                                    key=f'{trigger_validated.entity_type}:{self.event_message["key"]}',
                                    trigger_event_value=trigger_validated.json(),
                                )
                            case (False, trigger_invalidated):
                                self.handle_dql_message(
                                    key=self.event_message["key"],
                                    dlq_object=trigger_invalidated,
                                )

                except Exception as e:
                    logger.warning("failed to process trigger; Error: ", str(e))
                    self.handle_dql_message(key=str(e), dlq_object=str(e.args))
                    continue
                    # self.state_running = False

                finally:
                    match self.triggers_handler.ready_for_reprocessing():
                        case True:
                            self.handle_message_retried()

        finally:
            self.state_running = False
            self.consumer.close()

        return None

    def handle_dql_message(self, key: str, dlq_object: str):
        # TODO: Need more details and specifications here
        # to treat better the DLQ handling.
        print("Received a DLQ object: {}".format(dlq_object))
        self.producer.produce(
            self._conf.get_dlq_topic_name(), key=key, value=dlq_object
        )
        self.consumer.commit(asynchronous=False)

    def handle_message(self, key, trigger_event_value):
        """
        Description
        ----------

        After the trigger object has the schema validated, this function
        intends to pass the trigger to Foreman, if the Runners and workers
        have been available.

        Parameters
        ----------
        key : str
            Initial search path. If empty, the default search path is the
            caller's path.

        trigger_event_value : Any
            Represents the trigger key retrieved from the Broker.
            The value has the following pattern:
            TRIGGER:{{Connector}}:{{TriggerType}}:{{ObjectId}}

                Example: TRIGGER:Mellishops:635ca00b933d0d001e5da80b
        Returns:
        ----------
        None : Have no returns
        """
        event_trigger = {"key": key, "value": trigger_event_value}

        # That's the experimental function. Keeping for while.
        # self.triggers_handler.check_lock_exists_inside_list("triggers:trigger_queue")

        if self.triggers_handler.check_lock_exists(key=key):
            self.triggers_handler.enqueue_trigger_locked(self.event_message)
        else:
            match self.triggers_handler.trigger_dispatch(event_trigger):
                case True:
                    tp = self.__format_topic_partition__(
                        topic_name=self.event_message["topic_name"],
                        partition=self.event_message["partition"],
                        offset=self.event_message["offset"],
                    )
                    self.consumer.commit(offsets=[tp], asynchronous=False)
                    print("The python class is: {}".format(trigger_event_value))
                    # self.consumer.commit(offsets=)
        pass

    def handle_message_retried(self):
        """
        Description
        ----------

        After the trigger object has the schema validated, this function
        intends to pass the trigger to Foreman, if the Runners and workers
        have been available.

        Parameters
        ----------
        key : str
            Initial search path. If empty, the default search path is the
            caller's path.

        trigger_object_validated : Any
            Represents the trigger key retrieved from the Broker.
            The value has the following pattern:
            {{Asset}}:{{TriggerType}}:{{ObjectId}}

                Example: TRIGGER:VibeAsset:635ca00b933d0d001e5da80b
        Returns:
        ----------
        None : Have no returns
        """

        print("Retried has been launched")

        for event_message in self.triggers_handler.trigger_queue.queue:
            if True:
                print(f"Added to the reprocessing QUEUE {event_message}")
                tp = self.__format_topic_partition__(
                    topic_name=self.event_message["topic_name"],
                    partition=self.event_message["partition"],
                    offset=self.event_message["offset"],
                )

                self.consumer.commit(offsets=[tp])
                self.triggers_handler.trigger_queue.dequeue()

        pass
