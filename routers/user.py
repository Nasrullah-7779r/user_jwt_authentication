import pdb
from fastapi import APIRouter, Depends, Form, Header, status, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import and_, func
from oauth2 import get_access_token, get_tokens, get_current_user, verify_access_token
from schemas import UserIn, UserInForUpdate, UserOut
from sqlalchemy.orm import Session
from db import get_db
from models import Note, User
import util
from jose import JWTError, jwt
from oauth2 import REFRESH_SECRET_KEY, ALGORITHM

router = APIRouter(tags=["User"])


@router.post('/register', status_code=status.HTTP_201_CREATED, response_model=UserOut)
def register_user(user:UserIn, db: Session = Depends(get_db) ):
       
       hashed_password = util.hash_password(user.password)
       user.password = hashed_password
       new_user = User(**user.model_dump())
       db.add(new_user)
       db.commit()
       return new_user
   

@router.post('/token', status_code=status.HTTP_201_CREATED)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(),  db: Session = Depends(get_db)):
       
       verified_user = db.query(User).filter(func.lower(User.name) == func.lower(user_credentials.username)).first()
       
       if verified_user is None:
              raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials")      
             
       if not util.verify_password(user_credentials.password, verified_user.password): # type: ignore
               raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=" credentials")
    
       token, refresh_token = get_tokens({"id":verified_user.id})
       
       return {"access_token": token, "refresh_token": refresh_token, "token_type": "bearer"}
       

@router.post('/refresh')
def refresh_token(refresh_token: str= Form(), access_token: str = Form()):
       print(refresh_token)
       print(access_token)
       try:  
           refresh_token_decoded = jwt.decode(refresh_token, REFRESH_SECRET_KEY, ALGORITHM)
           id_from_refresh = refresh_token_decoded.get('id')  # Extract user ID from refresh token
              
           new_access_token = get_access_token({"id": id_from_refresh})

           return {"access_token": new_access_token, "token_type": "bearer"}
       
       except JWTError:
           return {"error": "Invalid refresh token"}, status.HTTP_401_UNAUTHORIZED



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


@router.get('/users', response_model = list[UserOut])
def get_all_users(db: Session = Depends(get_db)):
      users= db.query(User).all()
      return users

@router.put('/update_user/{id}', status_code=status.HTTP_202_ACCEPTED)
def update_user(id: int, user_updated_info: UserInForUpdate, db: Session = Depends(get_db), user:int = Depends(get_current_user)):
              
       if id != user:
              raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized for requested action")
       
       user_to_update_q = db.query(User).filter(User.id == id)
       user_to_update = user_to_update_q.first()
       
       if user_to_update is None:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
       
       print(f"user to upade is {user_to_update}")
       user_to_update_q.update({"email": user_updated_info.email, "password": user_updated_info.password}, synchronize_session=False)
  
       # Commit changes to the database
       db.commit()
       db.refresh(user_to_update)
       return user_to_update



@router.delete('/delete_user/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_user(id: int, db: Session = Depends(get_db), user:int = Depends(get_current_user)):
       
       if id != user:
              raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized for requested action")
       
       user_to_delete_q = db.query(User).filter(User.id == id)
       user_to_delete = user_to_delete_q.first()
       
       if user_to_delete is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
       
       user_to_delete_q.delete()
       db.commit()
      

@router.get('/get_notes')
def get_notes(db: Session = Depends(get_db), user:int = Depends(get_current_user)):
      
       # if user_id != user:
       #        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized for requested action")
       
       notes = db.query(Note).filter(Note.owner_id == user).all()
       return notes