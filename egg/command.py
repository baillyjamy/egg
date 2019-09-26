import subprocess
from subprocess import Popen


class CmdError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


def cmd_exec(command: str):
    cmd = Command(command)
    cmd.start()
    status = cmd.wait()

    if status != 0:
        raise CmdError("An error occoured while executing %s" % command)


class Command:
    process: Popen

    def __init__(self, command: str):
        self.command = command
        self.pid = None

    def start(self):
        self.process = subprocess.Popen(self.command, stdout=subprocess.PIPE, shell=True)
        self.pid = self.process.pid

    def wait(self):
        self.process.wait()
        return self.process.returncode
