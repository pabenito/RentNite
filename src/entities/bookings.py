# Import libraries
from fastapi import APIRouter
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
async def search_id(id : str | None = None): 
    if id == None :
        return bookings.find
    else :
        return bookings.find({"_id": id})

@router.get("/search")
async def search_state(state : str | None = None):
    if state == None :
        return bookings.find
    else :
        return bookings.find({"state": state})

@router.post("/create")
async def create(from_ : int | None, state : str | None, to : int | None) :
    if from_ != None and state != None and to != None :
        bookings.insert_one({"from_": from_, "state": state, "to": to})
