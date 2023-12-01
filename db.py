from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from config import setting

DB_URL = f"{setting.database_server}://{setting.database_username}:{setting.database_password}@{setting.database_hostname}/{setting.database_name}"

engine = create_engine(DB_URL)

session = sessionmaker(autoflush=False, autocommit=False, bind=engine)

base = declarative_base()

def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()