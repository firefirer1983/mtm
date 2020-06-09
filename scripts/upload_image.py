import os
from pathlib import Path

from PIL import Image

from mtm.components.mood.auth import login_context
from mtm.components.mood.channels import MMChannel
from mtm.model.models import ImgStorageEntry

PREVIEW_WIDTH = 495
PREVIEW_HEIGHT = 675
IMG_REPO = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cache/img")
CWD = os.path.join(os.path.dirname(__file__))


def list_all_images():
    for dir_path in Path(IMG_REPO).iterdir():
        for img in Path(dir_path).iterdir():
            yield str(img)


def main():
    with login_context("18588232664", "123456") as token:
        channel = MMChannel(token)
        for img_path in list_all_images():
            ImgStorageEntry.insert_one(img_path)
            img = Image.open(img_path)
            upload_url, upload_key = channel.upload_image(img_path)
            img_out = img.resize((PREVIEW_WIDTH, PREVIEW_HEIGHT))
            img_out.save("resize.jpeg", "JPEG")
            preview_url, preview_key = channel.upload_image(os.path.join(CWD, "resize.jpeg"))
            ImgStorageEntry.finish_upload(
                file_name=os.path.basename(img_path),
                directory=os.path.dirname(img_path),
                url=upload_url,
                key=upload_key,
                preview_url=preview_url,
                preview_key=preview_key
            )


if __name__ == '__main__':
    main()
