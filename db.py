from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from config import setting
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from contextlib import asynccontextmanager

# Synchronous setup

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



# Asynchronous setup 
        
ASYNC_DB_URL = f"{setting.database_server}+asyncpg://{setting.database_username}:{setting.database_password}@{setting.database_hostname}/{setting.database_name}"

async_engine = create_async_engine(ASYNC_DB_URL, echo=True)

async_session= async_sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)


# async def get_async_db():
#     # async with async_engine.begin() as conn:
#     #      await conn.run_sync(base.metadata.create_all)
    
#     async_db = async_session()
#     try:
#         yield async_db
    
#     except Exception as e:
#                 print(e)
#                 await async_db.rollback()

#     finally:
#         await async_db.close()
