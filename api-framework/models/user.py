from pydantic import BaseModel, EmailStr

class User(BaseModel):
    username: str
    email: EmailStr | None = None

class UserCreate(BaseModel):
    username: str
    email: EmailStr | None = None
    password: str

class UserInDB(User):
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class LoginRequest(BaseModel):
    username: str
    password: str
