import pdb
from fastapi import APIRouter, Depends, status, HTTPException, Header
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import and_, func
from oauth2 import get_access_token, get_current_user, verify_access_token
from schemas import UserIn, UserOut, UserInForToken
from sqlalchemy.orm import Session
from db import get_db
from models import User


router = APIRouter(tags=["User"])


@router.post('/register', status_code=status.HTTP_201_CREATED, response_model=UserOut)
def register_user(user:UserIn, db: Session = Depends(get_db) ):
       
       new_user = User(**user.model_dump())
       db.add(new_user)
       db.commit()
       return new_user
   

@router.post('/token', status_code=status.HTTP_201_CREATED)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(),  db: Session = Depends(get_db)):
       
       verified_user_id = db.query(User).filter(and_(func.lower(User.name) == func.lower(user_credentials.username), User.password == user_credentials.password)).first()
       if verified_user_id is None:
              raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials")      
              # raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {id} is not found")
    
       token = get_access_token({"id":verified_user_id.id})
       
       return {"access_token": token, "token_type": "bearer"} 
       


@router.get('/test/{id}', status_code=status.HTTP_200_OK)
def test_user(id:int, user:int = Depends(get_current_user), db: Session = Depends(get_db)):

       if id == user:
            return {"message":"Hello world"}
       
       elif is_user_exist(id,db) is False: 
              raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not registered")
       else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not logged in")
            
       
def is_user_exist(id:int, db: Session = Depends(get_db)):
       user = db.query(User).filter(User.id==id).first()
       if user != None:
             return True
       return False
