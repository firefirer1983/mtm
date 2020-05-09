import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

log = logging.getLogger(__name__)

db_url = os.environ.get(
    "db", "mysql+pymysql://root:123456789@127.0.0.1:3306/mtm"
)
db_engine = create_engine(db_url)

Session = sessionmaker(bind=db_engine)


@contextmanager
def scoped_session(auto_commit=True):
    ssn = Session()
    try:
        yield ssn
        if auto_commit:
            ssn.commit()
    except Exception as e:
        ssn.rollback()
        raise
    finally:
        ssn.close()


class ScopedSession:
    def __init__(self, commit=True):
        self._session = Session()
        self._commit = commit

    def __enter__(self):
        return self._session

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type or exc_val or exc_tb:
            self._session.rollback()
        else:
            try:
                if self._commit:
                    self._session.commit()
            except Exception as e:
                log.exception(e)
                self._session.rollback()
                self._session.close()
                raise e
            finally:
                self._session.close()


class MyBase(declarative_base()):

    __abstract__ = True

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            if k not in self.columns:
                del kwargs[k]
        super().__init__(**kwargs)

    @property
    def columns(self):
        return [col.name for col in self.__table__.columns]

    def to_dict(self):
        return {col: getattr(self, col) for col in self.columns}
