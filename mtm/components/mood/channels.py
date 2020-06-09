import pdb
import time

import requests

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
    
    def release_mm(self, author, title, mm_entry_key, img_key, preview_key, duration,
                   style):
        release_note = {
            "author": author,
            "title": title,
            "cover": preview_key,
            "duration": str(duration),
            "sourceKey": mm_entry_key,
            "description": "",
            "backGround": img_key,
            "showStyle": style,
        }
        path_ = "/show"
        ret = requests.post(
            url=host + path_, json=release_note, auth=self._auth
        )
        pdb.set_trace()
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
    
    def upload_audio(self, audio):
        path_ = "/file/audio/upload"
        with open(audio, "rb") as f:
            ret = requests.post(
                host + path_, files={"file": f}, auth=self._auth
            )
        assert ret.status_code == 200, "upload audio fail"
        ret = ret.json()
        return ret["url"], ret["key"]
    
    def fake_upload_audio(self, audio):
        with open(audio, "rb") as f:
            assert f
            assert self
            time.sleep(1)
        return "fake upload_url", "fake_upload_key"
