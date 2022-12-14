# Import libraries
from fastapi import APIRouter, Query, status, HTTPException, Body
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
def get(
    sender_id: str | None = None, 
    house_id: str | None = None, 
    chat_id: str | None = None, 
    from_: date | None = None,
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

    result = []
    for message in messages_list:
        message: Message = message
        result.append(message.to_response())
    messages_list = result

    return messages_list

@router.post("/", status_code=status.HTTP_201_CREATED)
def post(message : MessagePost = Body(examples = 
    {
        "Chat message": {
            "value": {
                "sender_id": "string",
                "message": "string",
                "chat_id": "string"
            }
        },
        "House comment": {
            "value": {
                "sender_id": "string",
                "message": "string",
                "house_id": "string"
            }
        }, 
        "Response to another message": {
            "description" : "Can be a response to a chat message or to a house comment",
            "value": {
                "sender_id": "string",
                "message": "string",
                "response_to": "string"
            }
        }
    }
)):
    if not message.house_id and not message.chat_id and not message.response_to:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Messages needs a house_id, a chat_id or a response_to")
    if ((message.house_id and message.chat_id) 
        or (message.house_id and message.response_to) 
        or (message.chat_id and message.response_to)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Messages needs a house_id, a chat_id or a response_to, but only one of them")

    new_message: MessageConstructor = MessageConstructor()

    try:
        user: User = User.parse_obj(users.find_one({"_id": ObjectId(message.sender_id)}))
        new_message.sender_id = str(user.id)
        new_message.sender_username = user.username
    except: 
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"There is no user with that id: {message.sender_id}.")

    if message.house_id:
        try:
            house: House = House.parse_obj(houses.find_one({"_id": ObjectId(message.house_id)}))
            new_message.house_id = str(house.id)
        except: 
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"There is no house with that id: {message.house_id}.")
    
    if message.chat_id:
        try:
            chat: Chat = Chat.parse_obj(chats.find_one({"_id": ObjectId(message.chat_id)}))
            new_message.chat_id = str(chat.id)
        except: 
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"There is no chat with that id: {message.chat_id}.")
        if new_message.sender_id != chat.guest_id and new_message.sender_id != chat.owner_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=f"The sender must be the guest '{chat.guest_id}' or the owner '{chat.owner_id}' of the booking, but is: {message.sender_id}.")

    if message.response_to:
        try:
            response_to_message: Message = Message.parse_obj(messages.find_one({"_id": ObjectId(message.response_to)}))
            new_message.response_to = str(response_to_message.id)
            if response_to_message.chat_id:
                chat: Chat = Chat.parse_obj(chats.find_one({"_id": ObjectId(response_to_message.chat_id)}))
                new_message.chat_id = str(chat.id)
            if response_to_message.house_id:
                house: House = House.parse_obj(houses.find_one({"_id": ObjectId(response_to_message.house_id)}))
                new_message.house_id = str(house.id)
        except: 
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"There is no message with that id: {message.response_to}.")

    new_message.date = datetime.now(timezone("Europe/Madrid"))
    new_message.message = message.message

    inserted_message: InsertOneResult = messages.insert_one(jsonable_encoder(new_message.exclude_unset()))
    created_message: Message = Message.parse_obj(messages.find_one({"_id": ObjectId(inserted_message.inserted_id)}))

    return created_message.to_response()

@router.get("/{id}")
async def get_by_id(id: str):
    try:
        return Message.parse_obj(messages.find_one({"_id" : ObjectId(id)})).to_response()
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"There is no message with that id: {id}.")

@router.delete("/{id}")
def delete(id: str):
    try:
        message : Message = Message.parse_obj(messages.find_one_and_delete({"_id": ObjectId(id)}))
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"There is no message with that id: {id}.")

    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"There is no message with that id: {id}.")

    return message.to_response()
