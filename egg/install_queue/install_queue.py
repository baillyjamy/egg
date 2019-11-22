from collections import deque

from egg.install_queue.install_event import InstallEvent
from egg.singleton import Singleton


class InstallQueue(metaclass=Singleton):

    __queue = deque()

    def get(self):
        return self.__queue

    def getById(self, id: str):
        if len(self.__queue) > 0:
            return deque(filter(lambda x: id in x.id, self.__queue))
        return None

    def add(self, event: InstallEvent):
        self.__queue.append(event)
        return event.id

    def deleteById(self, id: str):
        if len(self.__queue) > 0:
            self.__queue = deque(filter(lambda x: x.id != id, self.__queue))

    def clearAllByEventType(self, event_type: InstallEvent.EventType):
        if len(self.__queue) > 0:
            self.__queue = deque(filter(lambda x: x.type is not event_type, self.__queue))

    def clearAll(self):
        if len(self.__queue) > 0:
            self.__queue.clear()

    def execLeft(self):
        self.__queue.popleft().exec()

    def execAll(self):
        if len(self.__queue) > 0:
            self.execLeft()
            self.execAll()
