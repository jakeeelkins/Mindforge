from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.models.user import User, UserCreate, Token
from app.services.auth_service import (
    create_user,
    authenticate_user,
    create_access_token,
    get_current_user,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


# JSON login model
class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate):
    return create_user(user)


@router.post("/token", response_model=Token)
def login(request: LoginRequest):
    user = authenticate_user(request.username, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    access_token = create_access_token({"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=User)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
