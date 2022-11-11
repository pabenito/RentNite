from pydantic import Field, EmailStr, BaseModel as PydanticBaseModel
from bson.objectid import ObjectId
from datetime import datetime
from enum import Enum
import uuid

# Define our BaseModel setting config

class BaseModel(PydanticBaseModel):
    class Config:
        arbitrary_types_allowed = True # In order to allow ObjectId

# Entities model

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