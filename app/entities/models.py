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
    longitude: float | None = None
    latitude: float | None = None


class MessageBase(BaseModel):
    sender_id: str
    sender_username: str
    date: datetime
    message: str
    response_to: str | None = None
    house_id: str | None = None
    chat_id: str | None = None

class ChatBase(BaseModel):
    house_address: AddressBase 
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
    image: str

class BookingBase(BaseModel):
    state: State
    from_: datetime
    to: datetime
    cost: float 
    guest_id: str
    guest_name: str
    house_id: str
    house_address: AddressBase
    meeting_location : AddressBase | None = None

class RatingBase(BaseModel):
    rater_id: str
    date: datetime  
    rated_user_id: str | None = None
    rated_user_Name: str | None = None
    rated_house_id: str | None = None
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
    street: str | None = None
    number: int | None = None
    city: str | None = None
    

class ChatConstructor(Simplifier):
    house_address: AddressBase | None
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
    password_hash: str | None  

class HouseConstructor(Simplifier):
    address: AddressConstructor | None = None
    capacity: int | None = None
    price: float | None = None
    rooms: int | None = None
    bathrooms: int | None = None
    owner_id: str | None = None
    image: str | None = None

class BookingConstructor(Simplifier):
    state: State | None = None
    from_: date | None = None
    to: date | None = None
    cost: float | None = None
    guest_id: str | None = None
    house_id: str | None = None
    meeting_location : AddressConstructor | None = None

class RatingConstructor(Simplifier):
    rater_id: str | None = None
    date: datetime | None = None
    rated_user_id: str | None = None
    rated_user_Name: str | None = None
    rated_house_id: str | None = None
    rate: int | None = None
    comment: str | None = None


# Models for post

class AddressPost(BaseModel):
    street: str
    number: int
    city: str
    
    
class RatingPost(BaseModel):
    rater_id: str 
    date: datetime 
    rated_user_id: str | None = None
    rated_user_Name: str | None = None
    rated_house_id: str | None = None
    rate: int 
    comment: str 

class ChatPost(BaseModel):
    booking_id : str

class MessagePost(BaseModel):
    sender_id: str
    message: str
    response_to: str | None = None
    house_id: str | None = None
    chat_id: str | None = None

class BookingPost(BaseModel):
    from_: date
    to: date
    cost: float
    guest_id: str
    house_id: str
    meeting_location : AddressPost | None = None

class HousePost(BaseModel):
    address: AddressPost 
    capacity: int 
    price: float 
    rooms: int 
    bathrooms: int 
    owner_id: str
    image: str

class UserPost(BaseModel):
    username: str 
    email: EmailStr 
    password_hash: str