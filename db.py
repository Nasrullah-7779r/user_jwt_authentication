from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from config import setting

# step 1 
DB_URL = f"{setting.database_server}://{setting.database_username}:{setting.database_password}@{setting.database_hostname}/{setting.database_name}"

# step 2
engine = create_engine(DB_URL)

# stpe 3 
session = sessionmaker(autoflush=False, autocommit=False, bind=engine)

# step 4 
base = declarative_base()

def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()