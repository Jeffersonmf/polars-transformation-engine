from datetime import datetime

from libs.modules.events.queue import Queue
from libs.repository.database.memory import Memory


class TriggersHandler(object):
    """
        Description
        -----------

        This module is responsible for effectively triggering the events received
        from the Broker to the next step in the Events flow.

    ​	[Call Foreman Module]
    """

    def __init__(self):
        self.trigger_queue = Queue()
        self.trigger_retries = 15
        self.last_retrie = datetime.now()
        self.storage = Memory()
        pass

    def enqueue_trigger_locked(self, trigger_event_message):
        self.trigger_queue.enqueue(trigger_event_message)
        pass

    def dequeue_trigger_locked(self):
        self.trigger_queue.dequeue()
        pass

    def trigger_dispatch(self, event_trigger) -> bool:
        try:
            is_trigger_saved: bool = self.storage.push_to_trigger_list(
                queue_name="triggers:trigger_queue", value=event_trigger["value"]
            )[0]

            if is_trigger_saved:
                is_trigger_saved = self.__lock_trigger__(event_trigger=event_trigger)

            return is_trigger_saved
        except Exception:
            return False

    def __lock_trigger__(self, event_trigger) -> bool:
        try:
            return self.storage.upsert_data(
                hkey=str.format("{}:{}", "LOCK", event_trigger["key"]),
                value="1",
            )[0]
        except Exception:
            return False

    def check_lock_exists(self, key) -> bool:
        return (
            True
            if len(self.storage.get_by_rowkey(hkey_name=f"LOCK:{key}")) > 0
            else False
        )

    # TODO: Create here a new function to check LOCK inside
    # a list instead Hash Key......
    def check_lock_exists_inside_list(self, key):
        for item in self.storage.get_list(key):
            print(item)

    def has_retries(self) -> bool:
        return True if (self.trigger_retries > 0) else False

    def ready_for_reprocessing(self) -> bool:
        # TODO: this function would be a event callback
        diff_seconds = datetime.now() - self.last_retrie

        # TODO: try to call a callback into another module from triggers...
        if self.has_retries() and diff_seconds.seconds > round(30):
            self.trigger_retries -= 1
            self.last_retrie = datetime.now()
            return True
        else:
            return False
