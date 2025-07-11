from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
from bson import ObjectId
from typing import Optional, Dict, Any, List

from Utility.PyObjectId import PyObjectId


class SocialLinks(BaseModel):
    model_config = ConfigDict(extra='allow')

    instagram: Optional[str] = None
    tiktok: Optional[str] = None


class Profile(BaseModel):
    model_config = ConfigDict(extra='allow')

    name: str
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    university: Optional[str] = None
    social_links: Optional[SocialLinks] = None


class UserResponse(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str, datetime: lambda v: v.isoformat()},
        extra='allow'
    )

    id: Optional[str] = Field(alias="_id", default=None)
    username: str
    email: EmailStr
    role: str
    profile: Profile
    created_at: datetime

    @field_validator('id', mode='before')
    @classmethod
    def convert_objectid_to_str(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str
    profile: Profile


# Modelo alternativo más flexible si el anterior no funciona
class FlexibleUserResponse(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str, datetime: lambda v: v.isoformat()},
        extra='allow'
    )

    id: Optional[str] = Field(alias="_id", default=None)
    username: str
    email: EmailStr
    role: str
    profile: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None

    @field_validator('id', mode='before')
    @classmethod
    def convert_objectid_to_str(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v


# Modelo User completo (con _id como PyObjectId)
class User(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    username: str
    email: EmailStr
    role: str
    profile: Profile
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

    @field_validator('id', mode='before')
    @classmethod
    def convert_objectid_to_str(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v

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
