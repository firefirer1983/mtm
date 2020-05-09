#!/usr/bin/env python3
from datetime import datetime
from sqlalchemy import DateTime, Column, Integer


class TimestampMixin:
    id = Column(Integer, autoincrement=True, primary_key=True)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        comment="更新时间",
    )
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
