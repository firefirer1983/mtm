from mtm.components.mood.auth import login_context
from mtm.components.mood.user import UserProfile
from mtm.model.database import scoped_session
from mtm.model.models import User


def main():
    with scoped_session(auto_commit=True) as s:
        users = s.query(User).filter_by(set_profile=False).all() or []
        for user in users:
            with login_context(user.phone, "123456") as token:
                
                profiler = UserProfile(auth=token)
                ret = profiler.update_profile(
                    nickname=user.nickname,
                    birthday=user.birthday.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    key=user.icon_key
                )
                user.set_profile = True


if __name__ == '__main__':
    main()
