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