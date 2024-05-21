import redis

from libs.configurations.redis_config import RedisConfig

# sys.path.append(os.path.split(os.path.abspath("configurations"))[0])


class Memory(object):
    """
    Description
    ----------
    This class is intended to provide support for interacting
    with our in-memory repository. [Redis]

    Through the Memory Repository [Redis], we communicate with
    other steps and modules of the flow,
    by asynchronous events, including the lock control [FIFO].
    """

    QUEUE_NAME = "triggers:trigger_queue"

    def __init__(self):
        self._conf = RedisConfig()
        self._conn = redis.Redis(str(self._conf.get_host()))

    def get_by_rowkey(self, hkey_name):
        return self._conn.hgetall(hkey_name)

    def get_list(self, name_list: str):
        return self._conn.lrange(name_list, 0, -1)

    def push_to_trigger_list(self, queue_name: str, value: str) -> tuple[(bool, str)]:
        data = self._conn.rpush(queue_name, value)
        return (True, str(data))

    def upsert_data(self, hkey: str, value: str) -> tuple[(bool, str)]:
        transaction_commited = False

        try:
            transaction_commited = bool(self._conn.hset(hkey, hkey, value))
        except Exception as e:
            return (False, str(e.args))
        finally:
            return (transaction_commited, hkey)

    def load_connectors(self) -> list:
        list_elements = self._conn.lrange(self.QUEUE_NAME, 0, -1)
        list_elements = [element.decode("utf-8") for element in list_elements]
        # Print the elements
        print("List elements:", list_elements)

        return list_elements
