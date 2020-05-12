import requests
from . import host


class Playlist:
    def __init__(self, auth):
        self._auth = auth

    def list_mine(self):
        path_ = "/show/mine"
        plist = requests.get(url=host + path_, auth=self._auth)
