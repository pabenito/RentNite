# Import libraries
from fastapi import APIRouter, Query, status, HTTPException
from fastapi.encoders import jsonable_encoder
from pymongo.collection import Collection
from pymongo.results import InsertOneResult
from datetime import datetime, date, time
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
        result.append(Message.parse_obj(message_dict))

    messages_list = result

    if sender_id:
        result = []
        for message in messages_list:
            message : Message = message
            if message.sender_id == sender_id:
                result.append(message)
        messages_list = result

    if house_id:
        result = []
        for message in messages_list:
            message : Message = message 
            if message.house_id == house_id:
                result.append(message)
        messages_list = result

    if chat_id:
        result = []
        for message in messages_list:
            message : Message = message 
            if message.chat_id == chat_id:
                result.append(message)
        messages_list = result

    if from_:
        result = []
        for message in messages_list:
            message : Message = message 
            if message.date.timestamp() >= datetime.combine(from_, time.min).timestamp():
                result.append(message)
        messages_list = result

    if to:
        result = []
        for message in messages_list:
            message : Message = message 
            if message.date.timestamp() <= datetime.combine(to, time.max).timestamp():
                result.append(message)
        messages_list = result

    return messages_list

@router.post("/", status_code=status.HTTP_201_CREATED)
async def post(
    message: str, 
    sender_id: str = Query(alias="sender-id"), 
    response_to: str | None = Query(default=None, alias="response-to"),
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

    new_message: MessageConstructor = MessageConstructor()

    try:
        user: User = User.parse_obj(users.find_one({"_id": ObjectId(sender_id)}))
        new_message.sender_id = str(user.id)
        new_message.sender_username = user.username
    except: 
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"There is no user with that id: {sender_id}.")

    if house_id:
        try:
            house: House = House.parse_obj(houses.find_one({"_id": ObjectId(house_id)}))
            new_message.house_id = str(house.id)
        except: 
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"There is no house with that id: {house_id}.")
    
    if chat_id:
        try:
            chat: Chat = Chat.parse_obj(chats.find_one({"_id": ObjectId(chat_id)}))
            new_message.chat_id = str(chat.id)
        except: 
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"There is no chat with that id: {chat_id}.")

    if response_to:
        try:
            response_to_message: Message = Message.parse_obj(messages.find_one({"_id": ObjectId(response_to)}))
            new_message.response_to = str(response_to_message.id)
        except: 
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"There is no message with that id: {response_to}.")

    new_message.date = datetime.now(timezone("Europe/Madrid"))
    new_message.message = message

    inserted_message: InsertOneResult = messages.insert_one(jsonable_encoder(new_message))
    created_message: Message = Message.parse_obj(messages.find_one({"_id": ObjectId(inserted_message.inserted_id)}))

    return created_message

@router.get("/{id}")
async def get_by_id(id: str):
    try:
        return Message.parse_obj(messages.find_one({"_id" : ObjectId(id)})) 
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"There is no message with that id: {id}.")


