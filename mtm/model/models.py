import os

from sqlalchemy import (
    Boolean,
    String,
    Column,
    DECIMAL,
    DateTime
)

from mtm.model.database import db_engine
from mtm.utils.string_fmt import parse_ext
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
    icon = Column(String(256))
    icon_url = Column(String(255))
    icon_key = Column(String(255))
    set_profile = Column(Boolean, default=False)
    birthday = Column(DateTime)
    
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


class MMStorageEntry(MyBase, TimestampMixin):
    __tablename__ = "mm_storage_entry"
    origin = Column(String(32), default="youtube")
    unique_id = Column(String(32), nullable=True)
    directory = Column(String(255), nullable=False)
    file_ext = Column(String(8), nullable=False)
    file_name = Column(String(32), nullable=False, unique=True)
    duration = Column(DECIMAL(precision=18))
    uploaded = Column(Boolean, default=False)
    upload_url = Column(String(255), nullable=True)
    upload_key = Column(String(255), nullable=True)
    is_partial = Column(Boolean, nullable=False, default=False)
    title = Column(String(255), nullable=False)
    
    @property
    def full_path(self):
        return os.path.join(self.directory, self.file_name)
    
    def __str__(self):
        return "StorageEntry(%s) unique_id:%s" % (
            os.path.join(self.directory, self.file_name), self.unique_id)
    
    @classmethod
    def insert_one(cls, origin=origin, unique_id=unique_id,
                   full_path=full_path,
                   duration=duration, title="", is_partial=False):
        directory, file_name, file_ext = cls.parse_full_path(full_path)
        try:
            with scoped_session(auto_commit=True) as s:
                s.add(
                    MMStorageEntry(
                        origin=origin,
                        unique_id=unique_id,
                        duration=duration,
                        directory=directory,
                        file_name=file_name,
                        file_ext=file_ext,
                        title=title,
                        is_partial=is_partial
                    )
                )
        except Exception as e:
            print(e)
            return False
        return True
    
    @classmethod
    def parse_full_path(cls, val):
        return os.path.dirname(val), os.path.basename(val), parse_ext(val)
    
    @classmethod
    def finish_upload(cls, file_name, url, key):
        with scoped_session(auto_commit=True) as s:
            entry: MMStorageEntry = s.query(cls).filter_by(
                file_name=file_name).one()
            entry.upload_url = url
            entry.upload_key = key


class ImgStorageEntry(MyBase, TimestampMixin):
    __tablename__ = "img_storage_entry"
    directory = Column(String(255), nullable=False)
    file_ext = Column(String(8), nullable=False)
    file_name = Column(String(32), nullable=False, unique=True)
    uploaded = Column(Boolean, default=False)
    upload_url = Column(String(255), nullable=True)
    upload_key = Column(String(255), nullable=True)
    preview_url = Column(String(255), nullable=True)
    preview_key = Column(String(255), nullable=True)
    
    @property
    def full_path(self):
        return os.path.join(self.directory, self.file_name)
    
    def __str__(self):
        return "StorageEntry(%s) unique_id:%s" % (
            os.path.join(self.directory, self.file_name), self.unique_id)
    
    @classmethod
    def insert_one(cls, full_path=full_path):
        directory, file_name, file_ext = cls.parse_full_path(full_path)
        try:
            with scoped_session(auto_commit=True) as s:
                s.add(
                    ImgStorageEntry(
                        directory=directory,
                        file_name=file_name,
                        file_ext=file_ext,
                    )
                )
        except Exception as e:
            print(e)
            return False
        return True
    
    @classmethod
    def parse_full_path(cls, val):
        return os.path.dirname(val), os.path.basename(val), parse_ext(val)
    
    @classmethod
    def finish_upload(cls, file_name, url, key, preview_url, preview_key):
        with scoped_session(auto_commit=True) as s:
            entry: ImgStorageEntry = s.query(cls).filter_by(
                file_name=file_name).one()
            entry.upload_url = url
            entry.upload_key = key
            entry.preview_url = preview_url
            entry.preview_key = preview_key


def create_all_tables():
    print("create all tables")
    MyBase.metadata.create_all(db_engine)


def drop_all_tables():
    print("drop all tables!")
    MyBase.metadata.drop_all(db_engine)


if __name__ == '__main__':
    create_all_tables()
