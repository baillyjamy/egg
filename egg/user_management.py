import re

class UserManagement():
    def __init__(self):
        pass

    def check_validity_user_name(self, username) -> bool:
        if not username.strip():
            return False
        pattern = re.compile(r'[!^a-zA-Z0-9._\-]')
        res = pattern.sub('', username)
        if len(res) == 0:
            return True
        return False

    def check_validity_fullname(self, fullname) -> bool:
        if not fullname.strip():
            return False
        return True

    def check_validity_password(self, password) -> bool:
        if not password.strip():
            return False
        return True

    def get_recommanded_user_name(self, username) -> str:
        pattern = re.compile(r'[^a-zA-Z0-9._\-]')
        return pattern.sub('', username)
