from pydantic import BaseModel

class Goals(BaseModel):
    username: str
    month: int
    daily: int