from pydantic import BaseModel
from typing import Optional

# Auth Token
class Token(BaseModel):
    access_token: str
    token_type: str

# Data for Auth Token
class TokenData(BaseModel):
    user_id: Optional[int] = None