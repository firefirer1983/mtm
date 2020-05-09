from mtm.model.models import User
from mtm.model.database import scoped_session
from faker import Faker

usernames = ["naeidzwwwwzlzzzz", "一个无聊的透明人", "金小柚126", "阿阿9雪阿阿", "马达加斯加的海狸"]


def main():
    fk = Faker("zh_CN")
    for username in usernames:
        if not User.is_user_exist(username):
            with scoped_session(auto_commit=True) as ssn:
                user = User(
                    username=username,
                    phone=fk.phone_number(),
                    password="Fyman123",
                    nickname=username,
                    icon="%s.jpg" % username,
                    disable=False,
                )
                user.save(ssn)
                print("save:%s" % username)


if __name__ == "__main__":
    main()
