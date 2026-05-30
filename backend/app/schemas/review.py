from datetime import datetime
from typing import Optional

from pydantic import BaseModel, validator


class CommentCreate(BaseModel):
    content: str
    parent_id: Optional[int] = None


class CommentOut(BaseModel):
    id: int
    user_id: int
    user_name: str
    user_avatar: str = ""
    user_role: str = "student"
    parent_id: Optional[int] = None
    content: str
    created_at: datetime

    class Config:
        orm_mode = True


class RatingCreate(BaseModel):
    stars: int

    @validator("stars")
    def valid_stars(cls, v):
        if v < 1 or v > 5:
            raise ValueError("Số sao phải từ 1 đến 5")
        return v


class RatingSummary(BaseModel):
    average: float
    count: int
    my_rating: int = 0
