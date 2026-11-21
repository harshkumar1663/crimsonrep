from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from CrimsonRep.core.database import SessionLocal
from CrimsonRep.core.security import SECRET_KEY, ALGORITHM
from CrimsonRep.models.user import User

# Tell FastAPI to look for a token in the Auth header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str= Depends(oauth2_scheme),
                     db: Session= Depends(get_db)) -> User:
    credentials_exception= HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, 
        detail= "Could not validate credentials",   
    )
    try:
        # decode the jwt
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # 2 fetch user from DB
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception

    return user
