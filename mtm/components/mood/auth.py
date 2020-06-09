from contextlib import contextmanager

import requests
from faker import Faker

from mtm.components.mood import host

fk = Faker("zh_CN")


class LoginMethod:
    VERIFICATION_CODE = "VERIFICATION_CODE"
    PASSWORD = "PASSWORD"


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
    def bearer(self):
        return self._bearer
    
    @property
    def token(self):
        return self._token
    
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
        assert ret.status_code == 200
        body = ret.json()
        self._token = body["token"]
        self._bearer = BearerAuth(self._token)
        self._login = bool(self._token)
        return ret.status_code == 200
    
    def logout(self):
        path_ = "/user/logout"
        ret = requests.post(url=host + path_, auth=self.bearer)
        return ret.status_code == 200


@contextmanager
def login_context(username, password_or_code):
    auth = Auth(username, password_or_code=password_or_code)
    assert auth.login(), "Login failed!"
    yield auth.bearer
    auth.logout()
