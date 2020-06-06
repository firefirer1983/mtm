import os

from sqlalchemy import (
    Boolean,
    String,
    Column,
    DECIMAL

)

from mtm.model.database import db_engine
from .database import MyBase, scoped_session, USE_SQLITE
from .mixin import TimestampMixin

if USE_SQLITE:
    from .type_decoder import SqliteNumeric as DECIMAL


class MediaLocation:
    origin = "origin"
    cache = "cache"
    repo = "repo"


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


class StorageEntry(MyBase, TimestampMixin):
    __tablename__ = "storage_entry"
    unique_id = Column(String(32), nullable=True)
    directory = Column(String(255), nullable=False)
    file_ext = Column(String(8), nullable=False)
    file_name = Column(String(32), nullable=False, unique=True)
    duration = Column(DECIMAL)
    
    def full_path(self):
        return os.path.join(self.directory, self.file_name)
    
    def __str__(self):
        return "StorageEntry(%s) unique_id:%s" % (
            os.path.join(self.directory, self.file_name), self.unique_id)


def create_all_tables():
    print("create all tables")
    MyBase.metadata.create_all(db_engine)


def drop_all_tables():
    print("drop all tables!")
    MyBase.metadata.drop_all(db_engine)


if __name__ == '__main__':
    create_all_tables()
