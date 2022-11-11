from pydantic import Field, EmailStr, BaseModel
from bson.objectid import ObjectId
from datetime import datetime
from enum import Enum
import uuid

# Enums

class State(Enum):
    ACCEPTED = "Accepted"
    DECLINED = "Declined"
    REQUESTED = "Requested"
    CANCELLED = "Cancelled"

# Define our ConfigModel for setting config

class ConfigModel(BaseModel):
    class Config:
        arbitrary_types_allowed = True # In order to allow ObjectId

# Base models

class MessageBase(BaseModel):
    sender_id: str
    sender_username: str
    date: datetime
    message: str
    response_to: str | None = None
    house_id: str | None = None
    chat_id: str | None = None

class ChatBase(BaseModel):
    house_address: str 
    booking_from: datetime
    booking_to: datetime
    booking_id : str 
    owner_id : str 
    owner_username : str 
    guest_id : str 
    guest_username : str

class UserBase(BaseModel):
    username: str
    email: EmailStr  

class HouseBase(BaseModel):
    address: str 
    capacity: int 
    price: int 
    rooms: int 
    bathrooms: int 
    owner_name: str = Field(alias="ownerName")

class BookingBase(BaseModel):
    state: State
    from_: datetime
    to: datetime 
    cost: int 
    user_name: str = Field(alias="userName")
    house_id: str = Field(alias="houseId")
    house_address: str = Field(alias="houseAddress")

# Entities models

class Message(MessageBase, ConfigModel):
    id: ObjectId = Field(alias="_id", default_factory=uuid.uuid4)

class Chat(ChatBase, ConfigModel):
    id: ObjectId = Field(alias="_id", default_factory=uuid.uuid4)

class User(UserBase, ConfigModel):
    id: ObjectId = Field(alias="_id", default_factory=uuid.uuid4)

class House(HouseBase, ConfigModel):
    id: ObjectId = Field(alias="_id", default_factory=uuid.uuid4)

class Booking(BookingBase, ConfigModel):
    id: ObjectId = Field(default_factory=uuid.uuid4, alias="_id")

# Response models

class MessageResponse(MessageBase):
    id: str

class ChatResponse(ChatBase):
    id: str

class UserResponse(UserBase):
    id: str

class HouseResponse(HouseBase):
    id: str

class BookingResponse(BookingBase):
    id: str

# Constructors models (allows None in all field in order to add them one by one)

class ChatConstructor(BaseModel):
    house_address: str | None
    booking_from: datetime | None
    booking_to: datetime | None
    booking_id : str | None 
    owner_id : str | None 
    owner_username : str | None 
    guest_id : str | None 
    guest_username : str | None

class MessageConstructor(BaseModel):
    sender_id: str | None
    sender_username: str | None
    date: datetime | None
    message: str | None
    response_to: str | None = None
    house_id: str | None = None
    chat_id: str | None = None