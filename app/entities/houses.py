# Import libraries
from fastapi import APIRouter, HTTPException, status
from app.database import db
from bson.objectid import ObjectId
import re

# Create router
router = APIRouter()

# Initialize DB
houses = db["houses"]
bookings = db["bookings"]
users = db["users"]

# API


@router.get("/")
def get(address: str | None = None, capacity: int | None = None, price: float | None = None, rooms: int | None = None,
        bathrooms: int | None = None, ownerId: str | None = None, ownerName: str | None = None, image: str | None = None,
        latitude: float | None = None, longitude: float | None = None, offset: int = 0, size: int = 10):
    if offset < 0 or size <= 0:
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                            "Invalid offset or size.")

    filter = {"capacity": capacity, "price": price, "rooms": rooms, "bathrooms": bathrooms,
              "ownerId": ownerId, "image": image, "latitude": latitude, "longitude": longitude}
    filter = {k: v for k, v in filter.items() if v is not None}

    if address is not None:
        filter["address"] = {"$regex": re.compile(
            ".*" + address + ".*", re.IGNORECASE)}

    if ownerName is not None:
        filter["ownerName"] = {"$regex": re.compile(
            ".*" + ownerName + ".*", re.IGNORECASE)}

    return list(houses.find(filter, {"_id": 0}, skip=offset, limit=size))


@router.get("/{id}")
async def get_by_id(id: str):
    try:
        house = houses.find_one({"_id": ObjectId(id)}, {"_id": 0})
    except:
        house = None

    if house is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "House not found.")

    return house


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create(address: str, capacity: int, price: float, rooms: int, bathrooms: int,
                 ownerId: str, image: str, latitude: float, longitude: float):
    if capacity <= 0 or price < 0 or rooms <= 0 or bathrooms <= 0:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid parameters.")

    try:
        owner = users.find_one({"_id": ObjectId(ownerId)}, {
                               "_id": 0, "username": 1})
    except:
        owner = None

    if owner is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND,
                            "No user was found with the given ID.")

    houses.insert_one({"address": address, "capacity": capacity, "price": price, "rooms": rooms, "bathrooms": bathrooms,
                       "ownerId": ownerId, "ownerName": owner["username"], "image": image, "latitude": latitude, "longitude": longitude})


@router.put("/{id}")
async def update(id: str, address: str | None = None, capacity: int | None = None, price: float | None = None, rooms: int | None = None,
                 bathrooms: int | None = None, image: str | None = None, latitude: float | None = None, longitude: float | None = None):
    if ((capacity or 1) <= 0) or ((price or 1) < 0) or ((rooms or 1) <= 0) or ((bathrooms or 1) <= 0):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid parameters.")

    parameters = {"address": address, "capacity": capacity, "price": price, "rooms": rooms,
                  "bathrooms": bathrooms, "image": image, "latitude": latitude, "longitude": longitude}
    parameters = {k: v for k, v in parameters.items() if v is not None}

    if len(parameters) == 0:
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                            "No data was given to update the house.")

    try:
        house = houses.find_one_and_update(
            {"_id": ObjectId(id)}, {"$set": parameters})
    except:
        house = None

    if house is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "House not found.")


@router.delete("/{id}")
async def delete(id: str):
    try:
        house = houses.find_one_and_delete({"_id": ObjectId(id)})
    except:
        house = None

    if house is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "House not found.")


@router.get("/owner/{ownerName}/guests")
async def get_guests_by_owner_name(ownerName: str):
    ownerName = re.compile(".*" + ownerName + ".*",
                           re.IGNORECASE)  # type: ignore

    houses_ids = list(houses.find(
        {"ownerName": {"$regex": ownerName}}, {"_id": 1}))

    if len(houses_ids) == 0:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Owner name not found.")

    houses_ids = [{"houseId": str(house_id.get("_id"))}
                  for house_id in houses_ids]

    return list(bookings.distinct("guestName", {"$or": houses_ids}))
