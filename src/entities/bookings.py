# Import libraries
from fastapi import Depends, APIRouter
from database import db as db

# Create router
router = APIRouter()

# Initialize DB
bookings = db["bookings"]

# API
@router.get("/")
async def root():
    return bookings.find

@router.get("/search")
async def searchid(id : str | None = None): 
    if id == None :
        return bookings.find
    else :
        return bookings.find({"_id": id})

@router.get("/search")
async def search(state : str | None = None):
    if state == None :
        return bookings.find
    else :
        return bookings.find({"state": state})
