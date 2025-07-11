from datetime import datetime

import bcrypt
from fastapi import APIRouter, HTTPException
from fastapi import FastAPI
from starlette import status
from starlette.responses import JSONResponse

from models.aggregates import UserResponse, FlexibleUserResponse, Post, Comment, Subscription, Message, UserCreate, PostCreate, CommentCreate, \
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


@router.get("/api/users/debug")
async def debug_users():
    try:
        users = await db.users.find({}, {"password_hash": 0, "password": 0}).to_list(100)

        # Convertir ObjectId y datetime para JSON
        processed_users = []
        for user in users:
            if "_id" in user:
                user["_id"] = str(user["_id"])
            if "created_at" in user and isinstance(user["created_at"], datetime):
                user["created_at"] = user["created_at"].isoformat()
            processed_users.append(user)

        return JSONResponse(content={
            "total_users": len(processed_users),
            "users": processed_users
        })

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


# Ruta principal con FlexibleUserResponse
@router.get("/api/users", response_model=List[FlexibleUserResponse])
async def get_users():
    try:
        # Obtener usuarios excluyendo campos de contraseña
        users = await db.users.find(
            {},
            {"password_hash": 0, "password": 0}
        ).to_list(100)

        # Procesar usuarios
        processed_users = []
        for user in users:
            # Convertir ObjectId a string
            if "_id" in user:
                user["_id"] = str(user["_id"])

            # Asegurar que created_at esté presente
            if "created_at" not in user:
                user["created_at"] = datetime.utcnow()

            processed_users.append(user)

        return processed_users

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving users"
        )


# Ruta alternativa con UserResponse estricto
@router.get("/api/users/strict", response_model=List[UserResponse])
async def get_users_strict():
    try:
        users = await db.users.find(
            {},
            {"password_hash": 0, "password": 0}
        ).to_list(100)

        processed_users = []
        for user in users:
            # Verificar campos requeridos
            if "profile" not in user:
                continue

            if "created_at" not in user:
                user["created_at"] = datetime.utcnow()

            # Convertir ObjectId
            if "_id" in user:
                user["_id"] = str(user["_id"])

            processed_users.append(user)

        return processed_users

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving users"
        )


@router.post("/api/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    try:
        # Verificar si el usuario ya existe
        existing_user = await db.users.find_one({
            "$or": [
                {"username": user.username},
                {"email": user.email}
            ]
        })

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already exists"
            )

        # Convertir a dict usando model_dump en lugar de dict()
        user_dict = user.model_dump()

        # Hash de la contraseña
        password = user_dict.pop("password")
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
        user_dict["password_hash"] = password_hash.decode('utf-8')

        # Agregar timestamp
        user_dict["created_at"] = datetime.utcnow()

        # Insertar en la base de datos
        result = await db.users.insert_one(user_dict)

        # Obtener el documento insertado
        created_user = await db.users.find_one(
            {"_id": result.inserted_id},
            {"password_hash": 0, "password": 0}
        )

        # Convertir ObjectId
        if "_id" in created_user:
            created_user["_id"] = str(created_user["_id"])

        return created_user

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating user"
        )


@router.get("/api/users/{user_id}", response_model=FlexibleUserResponse)
async def get_user(user_id: str):
    try:
        if not ObjectId.is_valid(user_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user ID format"
            )

        user = await db.users.find_one(
            {"_id": ObjectId(user_id)},
            {"password_hash": 0, "password": 0}
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Convertir ObjectId
        if "_id" in user:
            user["_id"] = str(user["_id"])

        return user

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving user"
        )


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


