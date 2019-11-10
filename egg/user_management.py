import re
from enum import Enum


class UserManagementError(Enum):
    ERROR = 'error'
    OK = 'ok'


class UserManagementErrorDescription:
    type = UserManagementError.OK
    name = None

    def __init__(self, type, name):
        self.type = type
        self.name = name

    def set_event_pass(self, name=None) -> None:
        self.type = UserManagementError.OK
        if name is not None:
            self.name = name

    def set_event_error(self, name=None) -> None:
        self.type = UserManagementError.ERROR
        if name is not None:
            self.name = name


class UserManagement:
    @staticmethod
    def check_validity_user_name(username) -> bool:
        if not username.strip():
            return False
        pattern = re.compile(r'[!^a-zA-Z0-9._\-]')
        res = pattern.sub('', username)
        if len(res) == 0:
            return True
        return False

    @staticmethod
    def check_validity_fullname(fullname) -> bool:
        if not fullname.strip():
            return False
        return True

    @staticmethod
    def check_validity_password(password) -> bool:
        regex_events = [(UserManagementErrorDescription(UserManagementError.ERROR, 'error_validity_password1'), "(.*[a-z])"),
                        (UserManagementErrorDescription(UserManagementError.ERROR, 'error_validity_password2'), "(.*[A-Z])"),
                        (UserManagementErrorDescription(UserManagementError.ERROR, 'error_validity_password3'), "(.*[0-9])"),
                        (UserManagementErrorDescription(UserManagementError.ERROR, 'error_validity_password4'), "(.*[!@#$%^&])"),
                        (UserManagementErrorDescription(UserManagementError.ERROR, 'error_validity_password5'), "(.{8,})")]

        for current in regex_events:
            pattern = re.compile(current[1])
            match = pattern.match(password)
            if match:
                current[0].set_event_pass()
            else:
                current[0].set_event_error()

        return regex_events

    @staticmethod
    def get_recommanded_user_name(username) -> str:
        pattern = re.compile(r'[^a-zA-Z0-9._\-]')
        return pattern.sub('', username)
