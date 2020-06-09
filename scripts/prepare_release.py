import random

from mtm.model.database import scoped_session
from mtm.model.models import MMStorageEntry, User, ImgStorageEntry, \
    ReleaseRecord


def main():
    with scoped_session(auto_commit=True) as s:
        users = s.query(User).all()
        images = s.query(ImgStorageEntry).all()
        res = s.query(MMStorageEntry.unique_id) \
            .group_by(MMStorageEntry.unique_id)
        unique_id_groups = [r[0] for r in res]
        for index, unique_id in enumerate(unique_id_groups, start=1):
            entries = s.query(MMStorageEntry) \
                          .filter_by(unique_id=unique_id) \
                          .all() or []
            author = random.choice(users)
            img = images[index]
            for entry in entries:
                record = ReleaseRecord()
                record.author = author.phone
                record.nickname = author.nickname
                record.password_or_verify = author.password
                record.img_entry_url = img.upload_url
                record.img_entry_key = img.upload_key
                record.preview_url = img.preview_url
                record.preview_key = img.preview_key
                record.mm_entry_url = entry.upload_url
                record.mm_entry_key = entry.upload_key
                record.title = entry.title
                record.duration = entry.duration
                record.style = 1
                s.add(record)
                s.flush()


if __name__ == '__main__':
    main()
