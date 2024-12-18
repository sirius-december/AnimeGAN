from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    videos_left: Mapped[int] = mapped_column(nullable=False, default=5)
    photos_left: Mapped[int] = mapped_column(nullable=False, default=5)
