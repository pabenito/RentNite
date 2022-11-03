# Import libraries
from fastapi import APIRouter, Response
from database import db as db
from bson.objectid import ObjectId
from datetime import datetime, date, time
import re

# Create router
router = APIRouter()

# Initialize DB
bookings = db["bookings"]

# Save possible states for later
states = ["Accepted", "Declined", "Requested", "Cancelled"]


# API
@router.get("/")
async def root():
    return {"message": "Welcome to bookings microservice"}

@router.post("/")
async def create(response: Response, from_: date, to: date, cost: float, userName: str, houseId: str):
    from_ = datetime.combine(from_, time.min)
    to = datetime.combine(to, time.min)

    if cost > 0 and from_ < to:
        bookings.insert_one({"state": "Requested", "from_":  from_,
                            "to": to, "cost": cost, "userName": userName, "houseId": houseId})
        response.status_code = 201
    else:
        response.status_code = 400


@router.put("/{id}")
async def update(response: Response, id: str, state: str | None = None, from_: date | None = None, to: date | None = None, cost: float | None = None):
    if from_ is not None:
        from_ = datetime.combine(from_, time.min)
    if to is not None:
        to = datetime.combine(to, time.min)

    data = {"state": state, "from_": from_, "to": to, "cost": cost}
    data = {k: v for k, v in data.items() if v is not None}

    if len(data) == 0:
        response.status_code = 400
        return

    if (state is not None and state not in states) and (cost is not None and cost <= 0):
        response.status_code = 400
        return

    try:
        booking = bookings.find_one({"_id": ObjectId(id)})
        
        dfrom_ = from_ or booking["from_"]
        dto = to or booking["to"]
        
        if not dfrom_ < dto:
            response.status_code = 400
            return

        booking = bookings.find_one_and_update(
            {"_id": ObjectId(id)}, {"$set": data})
    except:
        booking = None

    if booking is None:
        response.status_code = 404


@router.get("/{id}")
async def get_by_id(response: Response, id: str):
    try:
        booking = bookings.find_one({"_id": ObjectId(id)}, {"_id": 0})
    except:
        booking = None

    if booking is None:
        response.status_code = 404
    else:
        return booking


@router.get("/userName/{userName}")
async def get_by_user_name(userName: str):
    userName = re.compile(".*" + userName + ".*",
                          re.IGNORECASE)  # type: ignore
    return [b for b in bookings.find({"userName": {"$regex": userName}}, {"_id": 0})]


@router.get("/house/{houseId}")
async def get_by_house_id(houseId: str):
    return [b for b in bookings.find({"houseId": houseId}, {"_id": 0})]


@router.get("/state/{state}")
async def get_by_state(response: Response, state: str):
    if state not in states:
        response.status_code = 400

    return [b for b in bookings.find({"state": state}, {"_id": 0})]


@router.get("/range/")
async def get_range(response: Response, size: int, offset: int = 0):
    if offset >= 0 and size > 0:
        return [b for b in bookings.find(projection={"_id": 0}, skip=offset, limit=size)]
    else:
        response.status_code = 400


@router.delete("/{id}")
async def delete(response: Response, id: str):
    try:
        booking = bookings.find_one_and_delete({"_id": ObjectId(id)})
    except:
        booking = None

    if booking is None:
        response.status_code = 404
