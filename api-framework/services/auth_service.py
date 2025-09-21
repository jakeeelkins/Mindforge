
from datetime import datetime, timedelta
from typing import Optional, Dict

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core import config
from app.models.user import User, UserCreate, UserInDB

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Fake "database"
_fake_users: Dict[str, UserInDB] = {}

def get_user(username: str) -> Optional[UserInDB]:
    return _fake_users.get(username)

def create_user(user_in: UserCreate) -> User:
    if user_in.username in _fake_users:
        raise HTTPException(status_code=400, detail="Username already exists")
    hashed = get_password_hash(user_in.password)
    udb = UserInDB(username=user_in.username, email=user_in.email, hashed_password=hashed)
    _fake_users[user_in.username] = udb
    return User(username=udb.username, email=udb.email)

def authenticate_user(username: str, password: str) -> Optional[UserInDB]:
    user = get_user(username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

# JWT
def create_access_token(data: dict, expires_minutes: int = config.ACCESS_TOKEN_EXPIRE_MINUTES) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)

def decode_token(token: str) -> dict:
    return jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])

# Replace OAuth2 with HTTPBearer
security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user(username)
    if user is None:
        raise credentials_exception
    return User(username=user.username, email=user.email)
