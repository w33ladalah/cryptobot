from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm.session import sessionmaker

from config.settings import config

engine = create_engine(config.SQLALCHEMY_DATABASE_URI)
Session = scoped_session(sessionmaker(bind=engine))


def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()
