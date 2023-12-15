from typing import List, Tuple
from sqlalchemy import Row, and_
from sqlalchemy.orm import Session, aliased
from fastapi import status, HTTPException

from models import DeVoteDetails, Note, UpVoteDetails, User, Vote

def is_note_exist(note_from_db):
    if note_from_db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return note_from_db

def is_user_allowed(note_from_db: Note, user:int, detail:str):        
    note_owner_id = note_from_db.owner_id
    if user == note_owner_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)
            

def is_user_allowed_for_no_of_voter(note_from_db: Note, user:int, detail:str):        
    note_owner_id = note_from_db.owner_id
    if user != note_owner_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)
            
def get_names_of_voters(voters: List[Row[Tuple[int, int]]], db:Session):
    
    voter_ids = [voter.voter_id for voter in voters]
    
    user_alias = aliased(User)
    voter_names = db.query(user_alias.name).filter(user_alias.id.in_(voter_ids)).all()
    
    names = [name[0] for name in voter_names]
    
    return names 



def has_devoted_earlier(db:Session, note_id:int, user:int):
    has_devoted =  db.query(DeVoteDetails).filter(and_(DeVoteDetails.note_id == note_id, DeVoteDetails.voter_id == user)).first()
    if has_devoted is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You already have devoted this note")
    

def has_upvoted_earlier(db:Session, note_id:int, user:int):
     has_devoted =  db.query(UpVoteDetails).filter(and_(UpVoteDetails.note_id == note_id, UpVoteDetails.voter_id == user))
     if has_devoted is not None:
        db.query(UpVoteDetails).filter(and_(UpVoteDetails.note_id == note_id, UpVoteDetails.voter_id == user)).delete()
        db.commit()

        # decreament by one in the Vote table to upate data current picture
        db.query(Vote).filter(Vote.note_id== note_id).update({Vote.no_of_upvote: Vote.no_of_upvote - 1})
        db.commit()