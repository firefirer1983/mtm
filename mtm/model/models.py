from mtm.model.database import MyBase, db_engine
from .mixin import TimestampMixin
from .database import MyBase
from sqlalchemy import Integer, DECIMAL, Boolean, String, Column


class TxStatus:
    validating = "validating"
    valid = "valid"
    invalid = "invalid"
    downloading = "downloading"
    downloaded = "downloaded"
    download_fail = "download_fail"
    uploading = "uploading"
    uploaded = "uploaded"
    upload_fail = "upload_fail"


class Transmission(MyBase, TimestampMixin):

    __tablename__ = "transmission"
    url = Column(String(256), nullable=False, unique=True)
    origin = Column(String(32), nullable=False)
    vid = Column(String(256))
    status = Column(String(16), nullable=False, default=TxStatus.validating)


def create_all_tables():
    print("create all tables")
    MyBase.metadata.create_all(db_engine)


def drop_all_tables():
    print("drop all tables")
    MyBase.metadata.drop_all(db_engine)
