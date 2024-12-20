import datetime

import sqlalchemy.sql.sqltypes
from sqlalchemy import ForeignKey, DateTime, Column
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from telegram.database.constants import DEFAULT_VID_CNT, DEFAULT_IMAGE_CNT


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    videos_left: Mapped[int] = mapped_column(nullable=False, default=DEFAULT_VID_CNT)
    photos_left: Mapped[int] = mapped_column(nullable=False, default=DEFAULT_IMAGE_CNT)


class File(Base):
    __tablename__ = 'files'

    id: Mapped[str] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    date = Column(sqlalchemy.sql.sqltypes.Date, default=datetime.date.today())
