from datetime import datetime

from fastapi import APIRouter, HTTPException
from fastapi import FastAPI
from models.aggregates import User, Post, Comment, Subscription, Message, UserCreate, PostCreate, CommentCreate, \
    MessageCreate
from database import db
from bson import ObjectId
from typing import List

router = APIRouter()

from bson import ObjectId, Decimal128
from datetime import datetime

def transform_mongo_document(doc: dict) -> dict:
    def transform_value(v):
        if isinstance(v, ObjectId):
            return str(v)
        elif isinstance(v, datetime):
            return v.isoformat()
        elif isinstance(v, Decimal128):
            return float(v.to_decimal())
        elif isinstance(v, dict):
            return transform_mongo_document(v)
        elif isinstance(v, list):
            return [transform_value(i) for i in v]
        else:
            return v

    return {k: transform_value(v) for k, v in doc.items()}



@router.post("/api/users", response_model=User)
async def create_user(user: UserCreate):
    user_dict = user.dict()
    user_dict["password_hash"] = "hashed_" + user_dict.pop("password")
    result = await db.users.insert_one(user_dict)
    user_dict["_id"] = result.inserted_id
    return user_dict

@router.get("/api/users", response_model=List[User])
async def get_users():
    users = await db.users.find().to_list(100)
    for u in users:
        print(u)
    return users


@router.post("/api/posts", response_model=Post)
async def create_post(post: PostCreate):
    post_dict = post.dict()
    result = await db.posts.insert_one(post_dict)
    post_dict["_id"] = result.inserted_id
    return post_dict


@router.get("/api/posts", response_model=List[Post])
async def get_posts():
    posts = await db.posts.find().to_list(100)
    return [transform_mongo_document(post) for post in posts]


@router.delete("/api/posts/{post_id}")
async def delete_post(post_id: str):
    result = await db.posts.delete_one({"_id": ObjectId(post_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Post not found")
    return {"message": "Post deleted successfully"}

@router.post("/api/comments")
async def create_comment(comment: CommentCreate):
    comment_dict = comment.dict()
    result = await db.comments.insert_one(comment_dict)
    comment_dict["_id"] = str(result.inserted_id)
    return comment_dict



@router.get("/api/comments", response_model=List[Comment])
async def get_comments():
    comments = await db.comments.find().to_list(100)
    return [transform_mongo_document(c) for c in comments]


@router.post("/api/subscriptions", response_model=Subscription)
async def create_subscription(subscription: Subscription):
    sub_dict = subscription.dict()
    result = await db.subscriptions.insert_one(sub_dict)
    sub_dict["_id"] = result.inserted_id
    return sub_dict

@router.get("/api/subscriptions", response_model=List[Subscription])
async def get_subscriptions():
    subs = await db.subscriptions.find().to_list(100)
    return [transform_mongo_document(s) for s in subs]


@router.post("/api/messages")
async def send_message(message: MessageCreate):
    msg_dict = message.dict()
    result = await db.messages.insert_one(msg_dict)
    msg_dict["_id"] = str(result.inserted_id)
    return msg_dict


@router.get("/api/messages", response_model=List[Message])
async def get_messages():
    messages = await db.messages.find().to_list(100)
    return [transform_mongo_document(m) for m in messages]


