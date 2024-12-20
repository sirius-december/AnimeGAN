import os

import dotenv
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from telegram.database.entities import *

dotenv.load_dotenv()

engine = create_engine(os.environ['DATABASE_URL'], echo=True)
Base.metadata.create_all(engine)


def is_user_exists(user_id: int) -> bool:
    with Session(engine) as session:
        return session.query(User).where(User.id == user_id).scalar() is not None


def create_user_if_not_exists(user_id: int) -> User:
    if not is_user_exists(user_id):
        user = User(id=user_id)
        with Session(engine) as session:
            session.add(user)
            session.commit()

    with Session(engine) as session:
        return session.query(User).where(User.id == user_id).scalar()


def decrement_videos_left(user_id: int) -> None:
    with Session(engine) as session:
        user = session.query(User).where(User.id == user_id).scalar()
        user.videos_left -= 1
        session.commit()


def decrement_photos_left(user_id: int) -> None:
    with Session(engine) as session:
        user = session.query(User).where(User.id == user_id).scalar()
        user.photos_left -= 1
        session.commit()


def is_file_exists(file_id: str) -> bool:
    with Session(engine) as session:
        return session.query(File).where(File.id == file_id).scalar() is not None


def get_file_by_id(file_id: str) -> File:
    with Session(engine) as session:
        return session.query(File).where(File.id == file_id).scalar()


def save_file(file_id: str, user_id: int) -> File:
    file = get_file_by_id(file_id)
    if file is not None:
        return file

    with Session(engine) as session:
        file = File(id=file_id, user_id=user_id)
        session.add(file)
        session.commit()

        return session.query(File).where(File.id == file_id).scalar()


def update_user_limits(user_id: int) -> None:
    with (Session(engine) as session):
        files = session.query(File).where(File.user_id == user_id).order_by(sqlalchemy.desc(File.date)).all()

        print(len(files))

        if len(files) == 0 or files[0].date >= datetime.date.today():
            return

        user = session.query(User).where(User.id == user_id).scalar()
        user.videos_left = DEFAULT_VID_CNT
        user.photos_left = DEFAULT_IMAGE_CNT

        session.commit()