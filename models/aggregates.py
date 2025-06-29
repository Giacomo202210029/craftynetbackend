from pydantic import BaseModel, EmailStr, Field
from bson import ObjectId
from typing import Optional
from typing import List

from Utility.PyObjectId import PyObjectId


# MODELS
class User(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    username: str
    email: EmailStr
    role: str  # 'artist' or 'patron'
    class Config:
        validate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class UserCreate(User):
    password: str

class Post(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    author_id: str
    title: str
    description: str
    media: List[dict] = []
    visibility: str
    likes: int = 0
    comments: int = 0
    class Config:
        validate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class PostCreate(BaseModel):
    author_id: str
    title: str
    description: str
    media: List[dict] = []
    visibility: str
    likes: int = 0
    comments: int = 0


class Comment(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    post_id: str
    user_id: str
    content: str
    class Config:
        validate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class CommentCreate(BaseModel):
    post_id: str
    user_id: str
    content: str


from typing import Optional

class Subscription(BaseModel):
    id: Optional[str] = Field(alias="_id")
    patron_id: str
    artist_id: str
    tier: Optional[str] = ""  # ⬅️ Esto evita el error
    price_usd: float
    status: str
    started_at: str
    renewal_date: str
    last_payment: dict
    class Config:
        validate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class Message(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    sender_id: str
    receiver_id: str
    content: str
    attachments: List[str] = []
    read: bool = False
    sent_at: str
    class Config:
        validate_by_name = True


        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class MessageCreate(BaseModel):
    sender_id: str
    receiver_id: str
    content: str
    attachments: List[str] = []
    read: bool = False
    sent_at: str
