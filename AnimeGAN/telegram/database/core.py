import os

import dotenv
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