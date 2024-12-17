import os

import dotenv

from telegram.database.entities import *

from sqlalchemy import create_engine

dotenv.load_dotenv()

engine = create_engine(os.environ['DATABASE_URL'], echo=True)
Base.metadata.create_all(engine)