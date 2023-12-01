import os
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from datetime import datetime, timedelta
from dotenv import load_dotenv
from config import setting
load_dotenv()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# SECRET_KEY = os.getenv("SECRET_KEY")
# ALGORITHM = os.getenv("ALGORITHM")
# ACCESS_TOKEN_EXPIRE_MINUTES_str = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
SECRET_KEY = setting.secret_key
ALGORITHM = setting.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES= setting.access_token_expire_minutes

some="3"
val=int(some)

def get_access_token(data:dict):
    
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES) # type: ignore
    
    to_encode.update({"exp":expire})
    encoded_jwt = jwt.encode(to_encode,SECRET_KEY,ALGORITHM) # type: ignore
    return encoded_jwt


def verify_access_token(token:str):

    excep_user_with_invalid_token = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="you're not authorized")
    try:
        payload = jwt.decode(token,SECRET_KEY,ALGORITHM) # type: ignore
    
        id = payload.get('id')
        if id != None:
            return id
        else:
            raise excep_user_with_invalid_token
    
    except JWTError as e:
        print(f"JWTError: {e}")


def get_current_user(token: str = Depends(oauth2_scheme)):

    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail="Could not validate token",
                                          headers={"www-Authenticate":"Bearer"}
                                          )
    
    verified_user_id = verify_access_token(token)
    
    if verified_user_id is None:
        raise credentials_exception
    # print(f"Verified User ID: {verified_user_id}")
    return verified_user_id