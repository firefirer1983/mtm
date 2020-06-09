from mtm.components.mood.auth import login_context
from mtm.components.mood.channels import MMChannel
from mtm.model.database import scoped_session
from mtm.model.models import ReleaseRecord


def main():
    with scoped_session(auto_commit=True) as s:
        records = s.query(ReleaseRecord).filter_by(released=False).all()
        for r in records:
            with login_context(r.author, r.password_or_verify) as token:
                channel = MMChannel(token)
                channel.release_mm(
                    author=r.author,
                    title=r.title,
                    mm_entry_key=r.mm_entry_key,
                    img_key=r.img_entry_key,
                    preview_key=r.preview_key,
                    duration=r.duration,
                    style=r.style
                )
                r.released = True
                s.flush()


if __name__ == '__main__':
    main()
