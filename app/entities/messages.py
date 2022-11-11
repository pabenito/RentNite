# Import libraries
from fastapi import APIRouter, Query, status, HTTPException
from fastapi.encoders import jsonable_encoder
from pymongo.collection import Collection
from pymongo.results import InsertOneResult
from datetime import datetime, date
from pytz import timezone
from app.database import db as db
from .models import *

# Create router
router = APIRouter()

# Initialize DB
messages: Collection = db["messages"]
chats: Collection = db["chats"]
users: Collection = db["users"]
houses: Collection = db["houses"]
bookings: Collection = db["bookings"]

# API
@router.get("/")
async def get(
    sender_id: str | None = Query(default=None, alias="sender-id"), 
    house_id: str | None = Query(default=None, alias="house-id"), 
    chat_id: str | None = Query(default=None, alias="chat-id"), 
    from_: date | None = Query(default=None, alias="from"),
    to: date | None = None
):
    messages_list: list = list(messages.find())
    result : list = []

    for message_dict in messages_list:
        result.append(Chat.parse_obj(message_dict))

    messages_list = result

    if sender_id:
        for message in messages_list:
            message : Message = message 
            if message.house_address is sender_id:
                result.append(message)
        messages_list = result

    if house_id:
        for message in messages_list:
            message : Message = message 
            if message.house_address is house_id:
                result.append(message)
        messages_list = result

    if chat_id:
        for message in messages_list:
            message : Message = message 
            if message.house_address is chat_id:
                result.append(message)
        messages_list = result

    if from_:
        for message in messages_list:
            message : Message = message 
            if message.date > from_:
                result.append(message)
        messages_list = result

    if to:
        for message in messages_list:
            message : Message = message 
            if message.date < to:
                result.append(message)
        messages_list = result

    return messages_list

@router.post("/", status_code=status.HTTP_201_CREATED)
async def post(
    message: str, 
    sender_id: str = Query(alias="sender-id"), 
    response_to: str | None = Query(default=None, alias="sender-id"),
    house_id: str | None = Query(default=None, alias="house-id"), 
    chat_id: str | None = Query(default=None, alias="chat-id")
):
    if not house_id and not chat_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Messages needs a house_id or a chat_id.")
    if house_id and chat_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Messages needs a house_id or a chat_id, but not both.")
    
    new_message: Message

    try:
        user: User = users.find_one({"_id": ObjectId(sender_id)})
        new_message.sender_id = user.id
        new_message.sender_username = user.username
    except: 
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"There is no user with that id: {sender_id}.")

    if house_id:
        try:
            house: House = houses.find_one({"_id": ObjectId(house_id)})
            new_message.house_id = house.id
        except: 
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"There is no house with that id: {house_id}.")
    
    if chat_id:
        try:
            chat: Chat = chats.find_one({"_id": ObjectId(chat_id)})
            new_message.chat_id = chat.id
        except: 
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"There is no chat with that id: {chat_id}.")

    if response_to:
        try:
            response_to_message: Message = messages.find_one({"_id": ObjectId(response_to)})
            new_message.response_to = response_to_message.id
        except: 
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"There is no message with that id: {response_to}.")

    new_message: Message
    new_message.date = datetime.now(timezone("Europe/Madrid"))
    new_message.message = message

    inserted_message: InsertOneResult = messages.insert_one(new_message)
    created_message: Message =  messages.messages.find_one({"_id": inserted_message.inserted_id})

    return created_message


