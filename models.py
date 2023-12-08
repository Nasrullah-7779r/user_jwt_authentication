from sqlalchemy import TIMESTAMP, Column, ForeignKey, Integer, String, text
from db import base

class User(base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    name=Column(String, nullable=False)
    email = Column(String, nullable=False)
    password = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))


class Note(base):
    __tablename__ = "note"

    id = Column(Integer, primary_key=True)
    title=Column(String, nullable=False)
    description = Column(String, nullable=False)
    owner_id = Column(Integer, ForeignKey("user.id", ondelete="cascade"),   nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))


class Vote(base):
    __tablename__ = "vote"

    note_id = Column(Integer, primary_key=True)
    no_of_upvote = Column(Integer, nullable=False)
    no_of_devote = Column(Integer, nullable=False)
    owner_id = Column(Integer, ForeignKey("user.id", ondelete="cascade"), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))


class UpVoteDetails(base):
    __tablename__ = "upvote_details"

    note_id = Column(Integer, nullable=False, primary_key=True) # primary key is not requried, but due to error I have to keep it 
    voter_id = Column(Integer, nullable=False)
    

class DeVoteDetails(base):
    __tablename__ = "devote_details"

    note_id = Column(Integer, nullable=False, primary_key=True) # primary key is not requried, but due to error I have to keep it 
    voter_id = Column(Integer, nullable=False)
    
