from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from datetime import datetime, timedelta
from config import setting

SECRET_KEY = setting.secret_key
REFRESH_SECRET_KEY = setting.refresh_secret_key
ALGORITHM = setting.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES= setting.access_token_expire_minutes
REFRESH_TOKEN_EXPIRE_DAYS = setting.refresh_token_expire_days

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_tokens(data:dict):
    
    # access token
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES) # type: ignore
    
    to_encode.update({"exp":expire})
    access_token = jwt.encode(to_encode,SECRET_KEY,ALGORITHM) # type: ignore
    
    # refresh token
    refresh_payload = {"id": data["id"]}
    refresh_expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_payload.update({"exp":refresh_expire})
    refresh_token = jwt.encode(refresh_payload,REFRESH_SECRET_KEY,ALGORITHM)

    return access_token,refresh_token


def get_access_token(data:dict):
    
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES) # type: ignore
    
    to_encode.update({"exp":expire})
    
    access_token = jwt.encode(to_encode,SECRET_KEY,ALGORITHM) 

    return access_token



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
