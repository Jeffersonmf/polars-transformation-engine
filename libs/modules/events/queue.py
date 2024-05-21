class Queue:
    """
    Description
    ----------

    This is a FIFO-type queue control module, which helps trigger_reader
    to control events for reprocessing.

    """

    def __init__(self):
        self.queue = []

    def enqueue(self, x):
        return self.queue.insert(0, x)

    def dequeue(self):
        return self.queue.pop()

    def isEmpty(self):
        return len(self.queue) == 0

    def front(self):
        return self.queue[-1]

    def rear(self):
        return self.queue[0]
