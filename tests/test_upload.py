import json
import os

cache_path = os.path.dirname(os.path.dirname(__file__)) + "/cache/youtube/"


def test_upload_img(channel):
    img = cache_path + "Class Of Madame Gazelle   Peppa Pig My First Album 8  Peppa Pig Songs  Kids Songs  Baby Songs-KV8nU2KfMao/KV8nU2KfMao.jpg"
    res = channel.upload_image(img)
    assert res, "upload fail!"
    assert res["key"], "No key"
    assert res["url"], "No url"


# def test_upload_audio(channel):
#     audio = cache_path + "Class Of Madame Gazelle   Peppa Pig My First Album 8  Peppa Pig Songs  Kids Songs  Baby Songs-KV8nU2KfMao/KV8nU2KfMao.m4a"
#     res = channel.upload_audio(audio)
#     assert res, "upload fail"
#     assert res["key"], "No key"
#     assert res["url"], "No url"


def test_release(channel):
    with open(
        cache_path + "Class Of Madame Gazelle   Peppa Pig My First Album 8  Peppa Pig Songs  Kids Songs  Baby Songs-KV8nU2KfMao/KV8nU2KfMao.info.json", "r", encoding="utf8"
    ) as f:
        info = json.loads(f.read())
    assert info["duration"]
    assert info["title"]
    assert info["description"]
    image_meta = channel.upload_image(
        cache_path + "Class Of Madame Gazelle   Peppa Pig My First Album 8  Peppa Pig Songs  Kids Songs  Baby Songs-KV8nU2KfMao/KV8nU2KfMao.jpg"
    )
    audio_meta = channel.upload_audio(
        cache_path + "Class Of Madame Gazelle   Peppa Pig My First Album 8  Peppa Pig Songs  Kids Songs  Baby Songs-KV8nU2KfMao/KV8nU2KfMao.m4a"
    )
    channel.release_mm(info, audio_meta=audio_meta, image_meta=image_meta)
