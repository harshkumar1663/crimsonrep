from pydantic import BaseModel, EmailStr

# For incoming data (POST /auth/signup)
class UserCreate(BaseModel):
    email:EmailStr
    password:str

# For outgoing data (API Responses)
class UserResponse(BaseModel):
    id:int
    email:str
    # Allows Schema to read SQLAlchemy DB Obj
    class Config:
        from_attributes= True