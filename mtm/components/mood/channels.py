import pdb

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
        assert ret.status_code == 200, "list mm fail"
        return ret.json()

    def release_mm(self, info_meta, audio_meta, image_meta):
        release_note = {
            "title": str(info_meta["title"]),
            "cover": str(image_meta["url"]),
            "duration": str(info_meta["duration"]),
            "description": str(info_meta["description"]),
            "downloadURL": str(audio_meta["url"]),
            "showStyle": "1",
        }
        path_ = "/show"
        ret = requests.post(
            url=host + path_, json=release_note, auth=self._auth
        )
        pdb.set_trace()
        assert ret.status_code == 200, "release mm fail"
        return ret.json()

    def upload_image(self, img):
        path_ = "/file/image/upload"
        with open(img, "rb") as f:
            ret = requests.post(
                host + path_, files={"file": f}, auth=self._auth
            )
        assert ret.status_code == 200, "upload image fail"
        return ret.json()

    def upload_audio(self, audio):
        path_ = "/file/audio/upload"
        with open(audio, "rb") as f:
            ret = requests.post(
                host + path_, files={"file": f}, auth=self._auth
            )
        assert ret.status_code == 200, "upload audio fail"
        return ret.json()
