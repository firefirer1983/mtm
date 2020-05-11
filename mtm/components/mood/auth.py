import requests
from faker import Faker

from mtm.components.mood import host

fk = Faker("zh_CN")


class LoginMethod:
    VERIFICATION_CODE = "VERIFICATION_CODE"
    PASSWORD = "PASSWORD"


import requests


class BearerAuth(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers["authorization"] = "Bearer " + self.token
        return r


class Auth:
    def __init__(self, username, password_or_code):
        self._username = username
        self._password_or_code = password_or_code
        self._login_method = LoginMethod.VERIFICATION_CODE
        self._token = None
        self._bearer = None
        self._login = False

    @property
    def bear(self):
        return self._bearer

    def login(self):
        path_ = "/user/login"
        ret = requests.post(
            url=host + path_,
            json={
                "account": self._username,
                "codeOrPassword": self._password_or_code,
                "loginType": LoginMethod.VERIFICATION_CODE,
            },
        )
        ret = ret.json()
        self._token = ret["token"]
        self._bearer = BearerAuth(self._token)
        self._login = bool(self._token)

    def logout(self):
        path_ = "/user/logout"
        ret = requests.post(url=host + path_, auth=self.bear)
        ret = ret.json()
        self._token = ret["token"]
        self._login = bool(self._token)

    @property
    def token(self):
        return self._token
