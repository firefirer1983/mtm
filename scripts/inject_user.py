import os
import time
from pathlib import Path

from faker import Faker

from mtm.components.mood.auth import login_context
from mtm.components.mood.channels import MMChannel
from mtm.model.database import scoped_session
from mtm.model.models import User
from mtm.utils.data_repo import get_nick_names

icon_repo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                              "cache/icon")

fk = Faker("zh_CN")


def fake_phone_num_gen():
    fake_phone_nums = set()
    
    def _f():
        while True:
            ret = fk.phone_number()
            if ret in fake_phone_nums:
                continue
            else:
                fake_phone_nums.add(ret)
                break
        return ret
    
    return _f


get_fake_phone = fake_phone_num_gen()


def upload_image_task(task_queue):
    pass


PASSWORD_OR_VERIFY = "123456"


def main():
    nicknames = get_nick_names()
    for index, file_path in enumerate(Path(icon_repo_path).iterdir()):
        try:
            phone, nickname, icon = get_fake_phone(), nicknames[index], str(
                file_path)
            print(phone, nickname, icon)
            with scoped_session(auto_commit=True) as s:
                user = User(
                    username=phone,
                    phone=phone,
                    icon=icon,
                    nickname=nickname,
                    password=PASSWORD_OR_VERIFY,
                    birthday=fk.date_between()
                )
                with login_context(phone, PASSWORD_OR_VERIFY) as token:
                    channel = MMChannel(token)
                    upload_url, upload_key = channel.upload_image(icon)
                user.icon_url = upload_url
                user.icon_key = upload_key
                s.add(user)
                time.sleep(0.3)
        
        except IndexError:
            break


if __name__ == '__main__':
    main()
