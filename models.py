from pydantic import BaseModel

class UserRepr(BaseModel):
    full_name: str