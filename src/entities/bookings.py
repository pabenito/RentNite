# Import libraries
from fastapi import APIRouter, Response
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from database import db as db
from bson.objectid import ObjectId
import re

# Create router
router = APIRouter()

# Initialize DB
bookings = db["bookings"]

# Save possible states for later
states = ["Accepted", "Declined", "Requested", "Cancelled"]


# API


@router.post("/")
async def create(response: Response, state: str, from_: float, to: float, cost: float, userName: str, houseId: str):
    if state in states and from_ > 0 and to > 0 and cost > 0:
        bookings.insert_one({"state": state, "from_": from_,
                            "to": to, "cost": cost, "userName": userName, "houseId": houseId})
        response.status_code = 201
    else:
        response.status_code = 400


@router.put("/{id}")
async def update(response: Response, id: str, state: str | None = None, from_: float | None = None, to: float | None = None, cost: float | None = None):
    data = {"state": state, "from_": from_, "to": to, "cost": cost}
    data = {k: v for k, v in data.items() if v is not None}

    for v in data.values():
        if state not in states or type(v) is float and (v <= 0):
            response.status_code = 400
            return

    if len(data) > 0:
        try:
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
