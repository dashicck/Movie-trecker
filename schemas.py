from pydantic import BaseModel
from typing import Optional

class MovieBase(BaseModel):
    title: str
    rating: Optional[float] = None
    comment: Optional[str] = None
    watched_status: Optional[str] = "Not Watched"

class MovieCreate(MovieBase):
    pass

class Movie(MovieBase):
    id: int

    class Config:
        orm_mode = True  #Позволяет работать с объектами SQLAlchemy
#uvicorn main:app --reload
