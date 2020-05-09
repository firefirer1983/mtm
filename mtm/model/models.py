from mtm.model.database import MyBase, db_engine
from .mixin import TimestampMixin
from .database import MyBase, scoped_session
from sqlalchemy.orm import relationship
from sqlalchemy import (
    Integer,
    DECIMAL,
    Boolean,
    String,
    Column,
    ForeignKey,
    Table,
)


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


class User(MyBase, TimestampMixin):
    __tablename__ = "user"
    username = Column(String(64), nullable=False, unique=True)
    phone = Column(String(64), nullable=False, unique=True)
    password = Column(String(64), nullable=False)
    nickname = Column(String(64), nullable=False)
    introduction = Column(String(512))
    icon = Column(String(256))
    registered = Column(Boolean, nullable=False, default=False)
    disable = Column(Boolean, default=False)

    def save(self, ssn):
        ssn.add(self)

    @classmethod
    def is_user_exist(cls, username):
        with scoped_session(auto_commit=False) as ssn:
            return bool(
                ssn.query(cls).filter_by(username=username).one_or_none()
            )

    @classmethod
    def get_user(cls, ssn, username):
        return ssn.query(cls).filter_by(username=username).one()


class Transmission(MyBase, TimestampMixin):

    __tablename__ = "transmission"
    url = Column(String(256), nullable=False, unique=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    origin = Column(String(32), nullable=False)
    vid = Column(String(256))
    status = Column(String(16), nullable=False, default=TxStatus.validating)

    user = relationship("User")

    def save(self, ssn):
        ssn.add(self)

    @classmethod
    def is_transmission_exist(cls, url):
        with scoped_session(auto_commit=False) as ssn:
            return bool(ssn.query(cls).filter_by(url=url).one_or_none())

    @classmethod
    def get_transmission(cls, ssn, url):
        return ssn.query(cls).filter_by(url=url).one()

    @classmethod
    def get_transmission_by_id(cls, ssn, tx_id):
        return ssn.query(cls).filter_by(id=tx_id).one()

    @property
    def is_valid(self):
        return not (
            self.status == TxStatus.validating
            or self.status == TxStatus.invalid
        )

    @property
    def is_downloaded(self):
        return self.status == TxStatus.downloaded

    @property
    def is_downloading(self):
        return self.status == TxStatus.downloading

    @property
    def is_download_fail(self):
        return self.status == TxStatus.download_fail

    @property
    def is_finished(self):
        return self.status == TxStatus.uploaded

    @property
    def is_uploading(self):
        return self.status == TxStatus.uploading

    @property
    def is_upload_fail(self):
        return self.status == TxStatus.upload_fail


def create_all_tables():
    print("create all tables")
    MyBase.metadata.create_all(db_engine)


def drop_all_tables():
    print("drop all tables!")
    MyBase.metadata.drop_all(db_engine)
