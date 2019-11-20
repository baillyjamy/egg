from abc import ABC, abstractmethod
from enum import Enum
import subprocess


class InstallEvent(ABC):

    class EventType(Enum):
        TEST = 0
        DISK = 1
        PARTITION = 2
        COMMAND = 3

    def __init__(self, event_type: EventType, method_name: str, **kwargs):
        self.type = event_type
        self.method_name = method_name
        self.kwargs = kwargs

    @abstractmethod
    def exec(self):
        pass


class BasicInstallCommandEvent(InstallEvent):

    def exec_command(self, command: str):
        try:
            subprocess.check_call(command, shell=True)
        except Exception as e:
            pass

    def __init__(self, method_name, **kwargs):
        super().__init__(InstallEvent.EventType.COMMAND, method_name, **kwargs)

    def exec(self):
        basic_instance = BasicInstallCommandEvent(self.method_name)
        getattr(basic_instance, self.method_name)(**self.kwargs)
