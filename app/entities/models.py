from typing import Union
from pydantic import Field, EmailStr, BaseModel
from bson.objectid import ObjectId
from datetime import datetime, date
from enum import Enum
from copy import deepcopy
import uuid

# Enums

class State(Enum):
    ACCEPTED = "Aceptada"
    DECLINED = "Rechazada"
    REQUESTED = "Solicitada"
    CANCELLED = "Cancelada"

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

class AddressBase(BaseModel):
    street: str
    number: int
    city: str
    longitude: Union[float, None] = None
    latitude: Union[float, None] = None


class MessageBase(BaseModel):
    sender_id: str
    sender_username: str
    date: datetime
    message: str
    response_to: Union[str, None] = None
    house_id: Union[str, None] = None
    chat_id: Union[str, None] = None

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
    password_hash: str  

class HouseBase(BaseModel):
    address: AddressBase
    capacity: int 
    price: float 
    rooms: int 
    bathrooms: int 
    owner_name: str
    owner_id: str
    image: Union[str, None] = None

class BookingBase(BaseModel):
    state: State
    from_: datetime
    to: datetime
    cost: float 
    guest_id: str
    guest_name: str
    house_id: str
    house_address: AddressBase
    meeting_location : Union[AddressBase, None] = None

class RatingBase(BaseModel):
    rater_id: str
    date: datetime  
    rated_user_id: Union[str, None] = None
    rated_user_Name: Union[str, None] = None
    rated_house_id: Union[str, None] = None
    rate: int
    comment: str

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

class AddressConstructor(BaseModel):
    street: Union[str, None] = None
    number: Union[int, None] = None
    city: Union[str, None] = None
    

class ChatConstructor(Simplifier):
    house_address: Union[AddressBase, None] = None
    booking_from: Union[datetime, None] = None
    booking_to: Union[datetime, None] = None
    booking_id : Union[str, None] = None 
    owner_id : Union[str, None] = None 
    owner_username : Union[str, None] = None 
    guest_id : Union[str, None] = None 
    guest_username : Union[str, None] = None

class MessageConstructor(Simplifier):
    sender_id: Union[str, None] = None
    sender_username: Union[str, None] = None
    date: Union[datetime, None] = None
    message: Union[str, None] = None
    response_to: Union[str, None] = None
    house_id: Union[str, None] = None
    chat_id: Union[str, None] = None

class UserConstructor(Simplifier):
    username: Union[str, None] = None
    email: Union[EmailStr, None] = None  
    password_hash: Union[str, None] = None

class HouseConstructor(Simplifier):
    address: Union[AddressConstructor, None] = None
    capacity: Union[int, None] = None
    price: Union[float, None] = None
    rooms: Union[int, None] = None
    bathrooms: Union[int, None] = None
    owner_id: Union[str, None] = None
    image: Union[str, None] = None

class BookingConstructor(Simplifier):
    state: Union[State, None] = None
    from_: Union[date, None] = None
    to: Union[date, None] = None
    cost: Union[float, None] = None
    guest_id: Union[str, None] = None
    house_id: Union[str, None] = None
    meeting_location : Union[AddressConstructor, None] = None

class RatingConstructor(Simplifier):
    rater_id: Union[str, None] = None
    date: Union[datetime, None] = None
    rated_user_id: Union[str, None] = None
    rated_user_Name: Union[str, None] = None
    rated_house_id: Union[str, None] = None
    rate: Union[int, None] = None
    comment: Union[str, None] = None


# Models for post

class AddressPost(BaseModel):
    street: str
    number: int
    city: str
    
    
class RatingPost(BaseModel):
    rater_id: str
    date: datetime
    rated_user_id: Union[str, None] = None
    rated_user_Name: Union[str, None] = None
    rated_house_id: Union[str, None] = None
    rate: int
    comment: str

class ChatPost(BaseModel):
    booking_id : str

class MessagePost(BaseModel):
    sender_id: str
    message: str
    chat_id: Union[str, None] = None
    response_to: Union[str, None] = None
    house_id: Union[str, None] = None

class BookingPost(BaseModel):
    from_: date
    to: date
    cost: float
    guest_id: str
    house_id: str
    meeting_location : Union[AddressPost, None] = None

class HousePost(BaseModel):
    address: AddressPost
    capacity: int
    price: float
    rooms: int
    bathrooms: int
    owner_id: str
    image: Union[str, None] = None

class UserPost(BaseModel):
    username: str
    email: EmailStr
    password_hash: str
