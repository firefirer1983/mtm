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


class MediaLocation:
    origin = "origin"
    cache = "cache"
    repo = "repo"


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
    releasing = "releasing"
    released = "released"
    release_fail = "release_fail"


class MultiMedia(MyBase, TimestampMixin):
    __tablename__ = "multimedia"
    mtype = Column(String(16), nullable=False)
    origin = Column(String(256), nullable=False)
    title = Column(String(64), nullable=False)
    cached_at = Column(String(64))
    url = Column(String(256))
    key = Column(String(16))
    present = Column(String(16))

    @classmethod
    def is_cached(cls, origin):
        with scoped_session(auto_commit=False) as ssn:
            return bool(
                ssn.query.filter_by(
                    origin=origin, present=MediaLocation.origin
                )
            )

    @classmethod
    def get_media_by_origin(cls, origin, ssn):
        return ssn.query(cls).filter_by(origin=origin).first()


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

    @classmethod
    def list_users(cls, ssn):
        return ssn.query(cls).all()


class Transmission(MyBase, TimestampMixin):

    __tablename__ = "transmission"
    user_id = Column(Integer, ForeignKey("user.id"))
    mm_id = Column(Integer, ForeignKey("multimedia.id"))
    status = Column(String(16), nullable=False)

    user = relationship("User")
    multimedia = relationship("MultiMedia")

    def save(self, ssn):
        ssn.add(self)

    @classmethod
    def is_transmission_exist(cls, multimedia, status):
        with scoped_session(auto_commit=False) as ssn:
            return bool(
                ssn.query(cls)
                .filter_by(mm_id=multimedia, status=status)
                .one_or_none()
            )

    @classmethod
    def get_transmission(cls, ssn, multimedia, status):
        return ssn.query(cls).filter_by(mm_id=multimedia, status=status).one()

    @classmethod
    def get_transmission_by_id(cls, ssn, tx_id):
        return ssn.query(cls).filter_by(id=tx_id).one()


def create_all_tables():
    print("create all tables")
    MyBase.metadata.create_all(db_engine)


def drop_all_tables():
    print("drop all tables!")
    MyBase.metadata.drop_all(db_engine)
