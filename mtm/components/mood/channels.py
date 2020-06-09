import time

import requests

from mtm.utils.string_fmt import filter_emoji
from . import host

DESCRIPTION_MAX_LEN = 50
SHOW_STYLE = "1"


class MMChannel:
    def __init__(self, auth):
        self._auth = auth
    
    def list_mm(self):
        path_ = "/show"
        ret = requests.get(
            url=host + path_, auth=self._auth
        )
        assert ret.status_code == 200, "list mm fail"
        return ret.json()
    
    def release_mm(self, info_meta, audio_meta, image_meta):
        desc = filter_emoji(
            str(info_meta["description"][:DESCRIPTION_MAX_LEN])
        )
        release_note = {
            "title": info_meta["title"],
            "cover": image_meta["url"],
            "duration": str(info_meta["duration"]),
            "description": desc,
            "downloadURL": audio_meta["url"],
            "showStyle": SHOW_STYLE,
        }
        path_ = "/show"
        ret = requests.post(
            url=host + path_, json=release_note, auth=self._auth
        )
        assert ret.status_code == 200, "release mm fail"
        return True
    
    def upload_image(self, img):
        path_ = "/file/image/upload"
        with open(img, "rb") as f:
            ret = requests.post(
                host + path_, files={"file": f}, auth=self._auth
            )
        assert ret.status_code == 200, "upload image fail"
        ret = ret.json()
        return ret["url"], ret["key"]
    
    # def upload_audio(self, audio):
    #     path_ = "/file/audio/upload"
    #     with open(audio, "rb") as f:
    #         ret = requests.post(
    #             host + path_, files={"file": f}, auth=self._auth
    #         )
    #     assert ret.status_code == 200, "upload audio fail"
    #     ret = ret.json()
    #     return ret["url"], ret["key"]
    
    def fake_upload_audio(self, audio):
        with open(audio, "rb") as f:
            assert f
            assert self
            time.sleep(1)
        return "fake upload_url", "fake_upload_key"
