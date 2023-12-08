import time
from fastapi import APIRouter
from sqlalchemy import and_, func
from db import get_db
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session, aliased
from models import DeVoteDetails, Note, UpVoteDetails, User, Vote
from oauth2 import get_current_user
from schemas import NoteIn, NoteOut

router = APIRouter(tags=["Vote"])


@router.post('/upvote/{note_id}', status_code=status.HTTP_202_ACCEPTED)
def upvote(note_id: int , db:Session = Depends(get_db), user:int = Depends(get_current_user)):
    
    # check:1) check either note is exist in db
    note_from_db = db.query(Note).filter(Note.id == note_id).first()
    if note_from_db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    
    note_owner_id = note_from_db.owner_id

    # check:2) return 403 if user try to upvote its own created vote
    if user == note_owner_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can't upvote the note you own")
    
    # check:3) if user try to upvote a note which is already upvoted by him, return him 400 
    has_upvoted =  db.query(UpVoteDetails).filter(and_(UpVoteDetails.note_id == note_id, UpVoteDetails.voter_id == user)).first()
    if has_upvoted is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You already have upvoted this note")
   
   
    # check:4) if user try to upvote a note which it had devoted earlier, then let him/her upvote but remove the previous devoted record of the same note
    has_devoted =  db.query(DeVoteDetails).filter(and_(DeVoteDetails.note_id == note_id, DeVoteDetails.voter_id == user)).first()
    if has_devoted is not None:
        db.query(DeVoteDetails).filter(and_(DeVoteDetails.note_id == note_id, DeVoteDetails.voter_id == user)).delete()
        db.commit()

        # decreament by one in the Vote table to upate data current picture
        db.query(Vote).filter(Vote.note_id== note_id).update({Vote.no_of_devote: Vote.no_of_devote - 1})
        db.commit()
   
    # Scernario 1: Check if the Vote table is empty
    is_empty = db.query(func.count().label('count')).select_from(Vote).scalar() == 0
    
    if is_empty is True:
         first_vote = {"note_id": note_id, "no_of_upvote":1 ,"no_of_devote":0 ,"owner_id": note_owner_id}
         first_vote_insert = Vote(**first_vote)
         db.add(first_vote_insert)
         db.commit()
         # enter details in Upvote table 
         upvote = {"note_id": note_id, "voter_id": user}
         upvote = UpVoteDetails(**upvote)
         db.add(upvote)
         db.commit()

         return
    
    # Scernario 2: if note is not exist in Vote table
    is_note_exist = db.query(Vote).filter(Vote.note_id == note_id).first()

    if is_note_exist is None:
        
        new_vote = {"note_id": note_id, "no_of_upvote":1 ,"no_of_devote":0 ,"owner_id": note_owner_id}
        new_vote_insert = Vote(**new_vote)
        db.add(new_vote_insert)
        db.commit()
        # enter details in Upvote table 
        upvote = {"note_id": note_id, "voter_id": user}
        upvote = UpVoteDetails(**upvote)
        db.add(upvote)
        db.commit()
        return    
    
    # Scernario 3: if note exists and have to be updated 
    db.query(Vote).filter(Vote.note_id == note_id).update({Vote.no_of_upvote: Vote.no_of_upvote + 1})
    db.commit()

    # enter details in Upvote table 
    upvote = {"note_id": note_id, "voter_id": user}
    upvote = UpVoteDetails(**upvote)
    db.add(upvote)
    db.commit()
    
    
    
         
@router.post('/devote/{note_id}', status_code=status.HTTP_202_ACCEPTED)
def devote(note_id: int , db:Session = Depends(get_db), user:int = Depends(get_current_user)):
    
    # check:1) check either note is exist in db
    note_from_db = db.query(Note).filter(Note.id == note_id).first()
    if note_from_db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    
    note_owner_id = note_from_db.owner_id

    # check:2) return 403 if user try to upvote its own created vote
    if user == note_owner_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can't devote the note you own")
    
    # check:3) if user try to devote a note which is already devoted by him, return him 400 
    has_devoted =  db.query(DeVoteDetails).filter(and_(DeVoteDetails.note_id == note_id, DeVoteDetails.voter_id == user)).first()
    if has_devoted is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You already have devoted this note")
    
    # check:4) if user try to devote a note which it had upvoted earlier, then let him/her devote but remove the previous upvoted record of the same note
    has_devoted =  db.query(UpVoteDetails).filter(and_(UpVoteDetails.note_id == note_id, UpVoteDetails.voter_id == user))
    if has_devoted is not None:
        db.query(UpVoteDetails).filter(and_(UpVoteDetails.note_id == note_id, UpVoteDetails.voter_id == user)).delete()
        db.commit()
        
        # decreament by one in the Vote table to upate data current picture
        db.query(Vote).filter(Vote.note_id== note_id).update({Vote.no_of_upvote: Vote.no_of_upvote - 1})
        db.commit()

    # Scernario 1: Check if the Vote table is empty
    is_empty = db.query(func.count().label('count')).select_from(Vote).scalar() == 0
    
    if is_empty is True:
         first_vote = {"note_id": note_id, "no_of_upvote":0 ,"no_of_devote":1 ,"owner_id": note_owner_id}
         first_vote_insert = Vote(**first_vote)
         db.add(first_vote_insert)
         db.commit()
         # enter details in Upvote table 
         devote = {"note_id": note_id, "voter_id": user}
         devote = DeVoteDetails(**devote)
         db.add(devote)
         db.commit()

         return
    
    
     # Scernario 2: if note is not exist in Vote table
    is_note_exist = db.query(Vote).filter(Vote.note_id == note_id).first()

    if is_note_exist is None:
        
        new_vote = {"note_id": note_id, "no_of_upvote":0 ,"no_of_devote":1 ,"owner_id": note_owner_id}
        new_vote_insert = Vote(**new_vote)
        db.add(new_vote_insert)
        db.commit()
        # enter details in Upvote table 
        devote = {"note_id": note_id, "voter_id": user}
        devote = DeVoteDetails(**devote)
        db.add(devote)
        db.commit()
        return    
   
    # Scernario 3: if note exists and have to be updated 
    db.query(Vote).filter(Vote.note_id == note_id).update({Vote.no_of_devote: Vote.no_of_devote + 1})
    db.commit()

    # enter details in Upvote table 
    devote = {"note_id": note_id, "voter_id": user}
    devote = DeVoteDetails(**devote)
    db.add(devote)
    db.commit()




@router.get('/no_of_upvote/{note_id}')
def no_of_upvotes(note_id:int, db:Session = Depends(get_db), user:int = Depends(get_current_user)):

    # check:1) check either note is exist in db 
    note_from_db = db.query(Note).filter(Note.id == note_id).first()
    if note_from_db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    
    # check:2) return 403 if user try to check no of upvote of a note which its not own
    note_owner_id = note_from_db.owner_id
    if user != note_owner_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can't see the upvote status of anyone else's note")
    
    upvotes = db.query(UpVoteDetails).filter(UpVoteDetails.note_id == note_id)
    no_of_upvotes = upvotes.count()
    
    return {f"You have {no_of_upvotes} upvote(s) for note (id: {note_id})"}


@router.get('/no_of_devote/{note_id}')
def no_of_devotes(note_id:int, db:Session = Depends(get_db), user:int = Depends(get_current_user)):

    # check:1) check either note is exist in db 
    note_from_db = db.query(Note).filter(Note.id == note_id).first()
    if note_from_db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    
    # check:2) return 403 if user try to check no of devote of a note which its not own
    note_owner_id = note_from_db.owner_id
    if user != note_owner_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can't see the devote status of anyone else's note")
    
    devotes = db.query(DeVoteDetails).filter(DeVoteDetails.note_id == note_id)
    no_of_devotes = devotes.count()
    
    return {f"You have {no_of_devotes} devote(s) for note (id: {note_id})"}


@router.get('/upvoter/{note_id}')
def get_upvoter(note_id:int, db:Session = Depends(get_db), user:int = Depends(get_current_user)):

    # check:1) check either note is exist in db 
    note_from_db = db.query(Note).filter(Note.id == note_id).first()
    if note_from_db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    
    # check:2) return 403 if user try to check no of upvote of a note which its not own
    note_owner_id = note_from_db.owner_id
    if user != note_owner_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can't see the upvote status of anyone else's note")
    
    # have passed parameters separetly in the query method to get records with duplicated note_id, passing just table name to query method returns deduplicated record. which is not required here
    # ref: https://docs.sqlalchemy.org/en/14/faq/sessions.html#faq-query-deduplicating

    voters = db.query(UpVoteDetails.note_id, UpVoteDetails.voter_id).filter(UpVoteDetails.note_id == note_id).all()
    voter_ids = [voter.voter_id for voter in voters]
    
    user_alias = aliased(User)
    voter_names = db.query(user_alias.name).filter(user_alias.id.in_(voter_ids)).all()
    
    names = [name[0] for name in voter_names]
    
    return names
    

@router.get('/devoter/{note_id}')
def get_devoter(note_id:int, db:Session = Depends(get_db), user:int = Depends(get_current_user)):

    # check:1) check either note is exist in db 
    note_from_db = db.query(Note).filter(Note.id == note_id).first()
    if note_from_db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    
    # check:2) return 403 if user try to check no of upvote of a note which its not own
    note_owner_id = note_from_db.owner_id
    if user != note_owner_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can't see the devote status of anyone else's note")
    
    # have passed parameters separetly in the query method to get records with duplicated note_id, passing just table name to query method returns deduplicated record. which is not required here
    # ref: https://docs.sqlalchemy.org/en/14/faq/sessions.html#faq-query-deduplicating

    voters = db.query(DeVoteDetails.note_id, DeVoteDetails.voter_id).filter(DeVoteDetails.note_id == note_id).all()
    voter_ids = [voter.voter_id for voter in voters]
    
    user_alias = aliased(User)
    voter_names = db.query(user_alias.name).filter(user_alias.id.in_(voter_ids)).all()
    
    names = [name[0] for name in voter_names]
    
    return names    