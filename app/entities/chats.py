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
chats: Collection = db["chats"]
users: Collection = db["users"]
houses: Collection = db["houses"]
bookings: Collection = db["bookings"]

# API
@router.get("/", response_model=list[ChatResponse])
async def get(
    booking_id: Union[str, None] = Query(default=None, alias="booking-id"), 
    owner_id: Union[str, None] = Query(default=None, alias="owner-id"), 
    guest_id: Union[str, None] = Query(default=None, alias="guest-id"), 
    owner_username: Union[str, None] = Query(default=None, alias="owner-username"),
    guest_username: Union[str, None] = Query(default=None, alias="guest-username"), 
    from_: Union[date, None] = Query(default=None, alias="from"),
    to: Union[date, None] = None
):
    chats_list: list = list(chats.find())
    result : list = []

    for chat_dict in chats_list:
        result.append(Chat.parse_obj(chat_dict))

    chats_list = result

    if booking_id: 
        result = []
        for chat in chats_list:
            chat : Chat = chat 
            if chat.booking_id == booking_id:
                result.append(chat)
        chats_list = result

    if owner_id: 
        result = []
        for chat in chats_list:
            chat : Chat = chat 
            if chat.owner_id == owner_id:
                result.append(chat)
        chats_list = result

    if guest_id: 
        result = []
        for chat in chats_list:
            chat : Chat = chat 
            if chat.guest_id == guest_id:
                result.append(chat)
        chats_list = result

    if owner_username:
        result = [] 
        for chat in chats_list:
            chat : Chat = chat 
            if chat.owner_username == owner_username:
                result.append(chat)
        chats_list = result

    if guest_username: 
        result = []
        for chat in chats_list:
            chat : Chat = chat 
            if chat.guest_username == guest_username:
                result.append(chat)
        chats_list = result

    if from_:
        result = []
        for chat in chats_list:
            chat : Chat = chat 
            if chat.booking_from.timestamp() >= datetime.combine(from_, time.min).timestamp():
                result.append(chat)
        chats_list = result

    if to:
        result = []
        for chat in chats_list:
            chat : Chat = chat 
            if chat.booking_to.timestamp() >= datetime.combine(to, time.max).timestamp():
                result.append(chat)
        chats_list = result

    result = []
    for chat in chats_list:
        chat: Chat = chat
        result.append(chat.to_response())
    chats_list = result

    return chats_list

@router.get("/user/{user_id}", response_model=list[ChatResponse])
def get_by_user_id(user_id: str):
    chats_list: list = list(chats.find())
    result : list = []

    for chat_dict in chats_list:
        result.append(Chat.parse_obj(chat_dict))
    chats_list = result

    result : list = []
    for chat in chats_list:
        chat : Chat = chat 
        if chat.guest_id == user_id:
            result.append(chat)
    chats_list = result

    for chat in chats_list:
        chat : Chat = chat 
        if chat.owner_id == user_id:
            result.append(chat)
    chats_list = result

    result = []
    for chat in chats_list:
        chat: Chat = chat
        result.append(chat.to_response())
    chats_list = result

    return chats_list

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ChatResponse)
def post(booking_id: str):    
    new_chat: ChatConstructor = ChatConstructor()

    try:
        booking : Booking = Booking.parse_obj(bookings.find_one({"_id": ObjectId(booking_id)}))
        new_chat.booking_id = str(booking.id) 
        new_chat.booking_from = booking.from_
        new_chat.booking_to= booking.to
        new_chat.guest_id = booking.guest_id
        new_chat.guest_username = booking.guest_name 
    except: 
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"There is no booking with that id: {booking_id}.")

    try:
        house: House = House.parse_obj(houses.find_one({"_id": ObjectId(booking.house_id)}))
        new_chat.house_address = f"{house.address.street}, {house.address.number}, {house.address.city}"
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

    inserted_chat: InsertOneResult = chats.insert_one(jsonable_encoder(new_chat.exclude_unset()))
    created_chat: Chat = Chat.parse_obj(chats.find_one({"_id": ObjectId(inserted_chat.inserted_id)}))

    return created_chat.to_response()

@router.get("/{id}", response_model=ChatResponse)
async def get_by_id(id: str):
    try:
        return Chat.parse_obj(chats.find_one({"_id" : ObjectId(id)})).to_response()
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"There is no chat with that id: {id}.")