from pydantic import Field, EmailStr, BaseModel
from bson.objectid import ObjectId
from datetime import datetime
from enum import Enum
from copy import deepcopy
import uuid

# Enums

class State(Enum):
    ACCEPTED = "Accepted"
    DECLINED = "Declined"
    REQUESTED = "Requested"
    CANCELLED = "Cancelled"

# Define our Entities and Plain models, differs in id type

class Simplifier(BaseModel):
    def exclude_unset(self) -> dict: 
        return self.dict(exclude_unset=True)

class Plain(Simplifier):
    id: str

class Entity(Simplifier):
    id: ObjectId = Field(alias="_id", default_factory=uuid.uuid4)

    class Config:
        arbitrary_types_allowed = True # In order to allow ObjectId

    def to_plain(self) -> Plain: 
        copy = deepcopy(self)
        copy.id = str(copy.id)
        return copy

    def to_response(self) -> dict: 
        return self.to_plain().dict(exclude_unset=True)

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

class RatingBase(BaseModel):
    rater_id: str
    date: datetime  
    rated_user_id: str | None = None
    reted_house_id: str | None = None
    rate: int

# Entities models

class Message(MessageBase, Entity):
    pass

class Chat(ChatBase, Entity):
    pass

class User(UserBase, Entity):
    pass

class House(HouseBase, Entity):
    pass

class Booking(BookingBase, Entity):
    pass

class Rating(RatingBase, Entity):
    pass

# Response models

class MessageResponse(MessageBase, Plain):
    pass

class ChatResponse(ChatBase, Plain):
    pass

class UserResponse(UserBase, Plain):
    pass

class HouseResponse(HouseBase, Plain):
    pass

class BookingResponse(BookingBase, Plain):
    pass

class RatingResponse(RatingBase, Plain):
    pass

# Constructors models (allows None in all field in order to add them one by one)

class ChatConstructor(Simplifier):
    house_address: str | None
    booking_from: datetime | None
    booking_to: datetime | None
    booking_id : str | None 
    owner_id : str | None 
    owner_username : str | None 
    guest_id : str | None 
    guest_username : str | None

class MessageConstructor(Simplifier):
    sender_id: str | None
    sender_username: str | None
    date: datetime | None
    message: str | None
    response_to: str | None = None
    house_id: str | None = None
    chat_id: str | None = None

class UserConstructor(Simplifier):
    username: str | None
    email: EmailStr | None  

class HouseConstructor(Simplifier):
    address: str | None 
    capacity: int | None 
    price: int | None 
    rooms: int | None 
    bathrooms: int | None 
    owner_name: str | None = Field(alias="ownerName")

class BookingConstructor(Simplifier):
    state: State | None
    from_: datetime | None
    to: datetime | None 
    cost: int | None 
    user_name: str | None = Field(alias="userName")
    house_id: str | None = Field(alias="houseId")
    house_address: str | None = Field(alias="houseAddress")

class RatingConstructor(Simplifier):
    rater_id: str | None 
    date: datetime | None 
    rated_user_id: str | None = None
    reted_house_id: str | None = None
    rate: int | None 