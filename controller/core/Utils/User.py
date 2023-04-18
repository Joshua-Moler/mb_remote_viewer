from enum import Enum


class UserSession:
    def __init__(self):
        self.user = None
        self.auth = UserAuth.NO_USER
        self.token = None


class UserAuth(Enum):
    NO_USER = 0
    BASIC_USER = 1
    PRIVELEGED_USER = 2
    ADMIN_USER = 3
