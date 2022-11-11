# Import libraries
from fastapi import APIRouter, Query, status, HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic import Field, EmailStr, BaseModel as PydanticBaseModel
from typing import Literal
from app.database import db as db
from pymongo.collection import Collection
from pymongo.results import InsertOneResult
from bson.objectid import ObjectId
from datetime import datetime, date
from pytz import timezone
from enum import Enum
from pydantic.dataclasses import dataclass
from pydantic.json import ENCODERS_BY_TYPE
import uuid

# Create router
router = APIRouter()

# Initialize DB
chats: Collection = db["chats"]
users: Collection = db["users"]
houses: Collection = db["houses"]
bookings: Collection = db["bookings"]

# declare Objectid as str
ENCODERS_BY_TYPE[ObjectId]=str

# Entities model

class BaseModel(PydanticBaseModel):
    class Config:
        arbitrary_types_allowed = True

class Message(BaseModel):
    id: ObjectId = Field(alias="_id", default_factory=uuid.uuid4)
    sender_id: str
    sender_username: str
    date: datetime
    message: str
    response_to: str | None = None
    house_id: str | None = None
    chat_id: str | None = None

class Chat(BaseModel):
    id: ObjectId = Field(alias="_id", default_factory=uuid.uuid4)
    house_address: str 
    booking_from: datetime
    booking_to: datetime
    booking_id : str 
    owner_id : str 
    owner_username : str 
    guest_id : str 
    guest_username : str

class ChatConstructor(BaseModel):
    house_address: str | None
    booking_from: datetime | None
    booking_to: datetime | None
    booking_id : str | None 
    owner_id : str | None 
    owner_username : str | None 
    guest_id : str | None 
    guest_username : str | None

class User(BaseModel):
    id: ObjectId = Field(alias="_id", default_factory=uuid.uuid4)
    username: str
    email: EmailStr  

class House(BaseModel):
    id: ObjectId = Field(alias="_id", default_factory=uuid.uuid4)
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
    id: ObjectId = Field(default_factory=uuid.uuid4, alias="_id")
    state: State
    from_: datetime
    to: datetime 
    cost: int 
    user_name: str = Field(alias="userName")
    house_id: str = Field(alias="houseId")
    house_address: str = Field(alias="houseAddress")


# API
@router.get("/")
async def get(
    house_address: str | None = Query(default=None, alias="house-address"),
    booking_id: str | None = Query(default=None, alias="booking-id"), 
    owner_id: str | None = Query(default=None, alias="owner-id"), 
    guest_id: str | None = Query(default=None, alias="guest-id"), 
    owner_username: str | None = Query(default=None, alias="owner-username"),
    guest_username: str | None = Query(default=None, alias="guest-username"), 
    from_: date | None = Query(default=None, alias="from"),
    to: date | None = None
):
    return list(chats.find())

@router.post("/", status_code=status.HTTP_201_CREATED)
async def post(
    booking_id: str = Query(alias="booking-id"), 
):    
    new_chat: ChatConstructor = ChatConstructor()

    try:
        booking : Booking = Booking.parse_obj(bookings.find_one({"_id": ObjectId(booking_id)}))
        new_chat.booking_id = str(booking.id) 
        new_chat.booking_from = booking.from_
        new_chat.booking_to= booking.to 
    except: 
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"There is no booking with that id: {booking_id}.")

    try:
        house: House = House.parse_obj(houses.find_one({"_id": ObjectId(booking.house_id)}))
        new_chat.house_address = house.address
    except: 
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"There is no house with that id: {house_id}.")

    try:
        owner: User = User.parse_obj(users.find_one({"username": house.owner_name}))
        new_chat.owner_id = str(owner.id) 
        new_chat.owner_username = owner.username
    except: 
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"There is no user with that username: {house.owner_name}.")

    try:
        guest: User = User.parse_obj(users.find_one({"username": booking.user_name}))
        new_chat.guest_id = str(guest.id) 
        new_chat.guest_username = guest.username
    except: 
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"There is no user with that username: {booking.user_name}.")

    inserted_chat: InsertOneResult = chats.insert_one(jsonable_encoder(new_chat))
    created_chat: Chat = Chat.parse_obj(chats.find_one({"_id": ObjectId(inserted_chat.inserted_id)}))

    return created_chat