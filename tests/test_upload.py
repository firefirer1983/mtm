import json
import os

cwd = os.path.dirname(__file__) + "/"

print(cwd)


def xtest_upload_img(channel):
    img = cwd + "/" + "test.jpg"
    res = channel.upload_image(img)
    assert res, "upload fail!"
    assert res["key"], "No key"
    assert res["url"], "No url"


def xtest_upload_audio(channel):
    audio = cwd + "/" + "test.mp3"
    res = channel.upload_audio(audio)
    assert res, "upload fail"
    assert res["key"], "No key"
    assert res["url"], "No url"


def test_release(channel):
    with open(cwd + "youtube/NLJcwbpkiJ0/NLJcwbpkiJ0.info.json", "r") as f:
        info = json.loads(f.read())
    assert info["duration"]
    assert info["title"]
    assert info["description"]
    image_meta = channel.upload_image(
        cwd + "youtube/NLJcwbpkiJ0/NLJcwbpkiJ0.jpg"
    )
    audio_meta = channel.upload_audio(
        cwd + "youtube/NLJcwbpkiJ0/NLJcwbpkiJ0.m4a"
    )
    channel.release_mm(info, audio_meta=audio_meta, image_meta=image_meta)
