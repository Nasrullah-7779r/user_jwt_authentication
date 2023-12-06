from fastapi import APIRouter
from db import get_db
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from models import Note
from oauth2 import get_current_user
from schemas import NoteIn, NoteOut

router = APIRouter(tags=["Note"])


@router.get('/all_notes')
def get_all_notes(db:Session = Depends(get_db)):
    notes = db.query(Note).all()
    return notes


@router.post('/create_note', response_model=NoteOut, status_code=status.HTTP_201_CREATED)
def create_note(note: NoteIn, db:Session = Depends(get_db), user:int = Depends(get_current_user)):
   
    newnote = {"title": note.title, "description": note.description, "owner_id": user, "created_at":note.created_at}
    new_note = Note(**newnote)

    db.add(new_note)
    db.commit()
    db.refresh(new_note)
    return new_note



@router.delete('/delete_note/{note_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_note(note_id:int, db:Session = Depends(get_db), user:int = Depends(get_current_user)):
    print(f"note id is{note_id}") 
    note = db.query(Note).filter(Note.id == note_id).first()
    print(f"note is{note}")
    if note is None:
        raise HTTPException(detail="Note not found", status_code=status.HTTP_404_NOT_FOUND)
    if note.owner_id != user: # type: ignore
        raise HTTPException(detail="Not authorized for requested action", status_code=status.HTTP_403_FORBIDDEN)
    
    db.delete(note)
    db.commit()