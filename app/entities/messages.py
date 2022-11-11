# Import libraries
from fastapi import APIRouter, Query, status, HTTPException
from pydantic import Field, EmailStr, BaseModel
from typing import Literal
from app.database import *
from pymongo.collection import Collection
from pymongo.results import InsertOneResult
from bson.objectid import ObjectId
from datetime import datetime, date
from pytz import timezone
from enum import Enum
import uuid, pydantic

# Create router
router = APIRouter()

# Initialize DB
messages: Collection = db["messages"]
chats: Collection = db["chats"]
users: Collection = db["users"]
houses: Collection = db["houses"]
bookings: Collection = db["bookings"]

# declare Objectid as str
pydantic.json.ENCODERS_BY_TYPE[ObjectId]=str

# Entities model

class Message(BaseModel):
    _id: str = Field(alias="_id", default_factory=uuid.uuid4)
    sender_id: str
    sender_username: str
    date: datetime
    message: str
    response_to: str | None = None
    house_id: str | None = None
    chat_id: str | None = None

class Chat(BaseModel):
    _id: str = Field(alias="_id", default_factory=uuid.uuid4)
    house_address: str 
    booking_from: date
    booking_to: date
    booking_id : str 
    owner_id : str 
    owner_username : str 
    guest_id : str 
    guest_username : str

class User(BaseModel):
    _id: str = Field(alias="_id", default_factory=uuid.uuid4)
    username: str
    email: EmailStr  

class House(BaseModel):
    _id: str = Field(alias="_id", default_factory=uuid.uuid4)
    address: str 
    capacity: int 
    price: int 
    rooms: int 
    bathrooms: int 
    owner_name: str = Field(alias="ownerName")

class State(Enum):
    ACCEPTED = "Accepted"
    DECLINED = "Declined"
    REQUESTED = "Requested"
    CANCELLED = "Cancelled"

class Booking(BaseModel):
    _id: str = Field(default_factory=uuid.uuid4, alias="_id")
    state: State
    from_: date
    to: date 
    cost: int 
    user_name: str = Field(alias="userName")
    house_id: str
    house_address: str = Field(alias="houseAddress")

# API
@router.get("/", response_model=list[Message])
async def get(
    sender_id: str | None = Query(default=None, alias="sender-id"), 
    house_id: str | None = Query(default=None, alias="house-id"), 
    chat_id: str | None = Query(default=None, alias="chat-id"), 
    from_: date | None = Query(default=None, alias="from"),
    to: date | None = None
):
    return list(bookings.find())

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


