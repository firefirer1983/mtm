import pdb

import requests

from . import host


class UserProfile:
    
    def __init__(self, auth):
        self._auth = auth
    
    def get_info(self):
        path_ = "/user/account-info"
        ret = requests.get(
            url=host + path_,  auth=self._auth,
        )
        assert ret.status_code == 200
        return ret.json()
    
    def update_profile(self, nickname, birthday, key):
        path_ = "/user/profile"
        profile = {
            "nickName": nickname,
            "birthday": birthday,
            "headPortrait": key
        }
        ret = requests.put(
            url=host + path_, auth=self._auth, json=profile
        )
        assert ret.status_code == 200, "update profile failed!"
        return ret.status_code == 200
