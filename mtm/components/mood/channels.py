import requests
from mtm.components.mood import host


class MMChannel:
    def __init__(self, auth):
        self._auth = auth

    def list_mm(self):
        path_ = "/show"
        ret = requests.get(
            url=host + path_, params={"bearer": self._auth.token}
        )
        ret = ret.json()