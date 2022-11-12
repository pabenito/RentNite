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

# API
@router.get("/")
async def get(address: str | None = None, capacity: int | None = None, price: float | None = None, rooms: int | None = None, 
              bathrooms: int | None = None, ownerName: str | None = None, offset: int = 0, size: int = 10):
    filter = {"capacity": capacity, "price": price, "rooms": rooms, "bathrooms": bathrooms}
    filter = {k: v for k, v in filter.items() if v is not None}

    if address is not None:
        filter["address"] = {"$regex": re.compile(".*" + address + ".*", re.IGNORECASE)}

    if ownerName is not None:
        filter["ownerName"] = {"$regex": re.compile(".*" + ownerName + ".*", re.IGNORECASE)}

    if offset < 0 or size <= 0:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid offset or size.")

    return list(houses.find(filter, {"_id": 0}, skip = offset, limit = size))

@router.get("/{id}")
async def get_by_id(id: str):
    try:
        house = houses.find_one({"_id": ObjectId(id)}, {"_id": 0})
    except:
        house = None

    if house is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "House not found.")

    return house

@router.post("/", status_code = status.HTTP_201_CREATED)
async def create(address: str, capacity: int, price: float, rooms: int, bathrooms: int, ownerName: str):
    if capacity <= 0 or price < 0 or rooms <= 0 or bathrooms <= 0 or not re.fullmatch("[a-zA-Z]+( [a-zA-Z]+)*", ownerName):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid parameters.")
    
    houses.insert_one({"address": address, "capacity": capacity, "price": price, 
                       "rooms": rooms, "bathrooms": bathrooms, "ownerName": ownerName})

@router.put("/{id}")
async def update(id: str, address: str | None = None, capacity: int | None = None, 
                 price: float | None = None, rooms: int | None = None, bathrooms: int | None = None):
    parameters = {"address": address, "capacity": capacity, "price": price, "rooms": rooms, "bathrooms": bathrooms}
    parameters = {k: v for k, v in parameters.items() if v is not None}

    if len(parameters) == 0:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "No data was given to update the house.")

    if ((capacity or 1) <= 0) or ((price or 1) < 0) or ((rooms or 1) <= 0) or ((bathrooms or 1) <= 0):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid parameters.")

    try:
        house = houses.find_one_and_update({"_id": ObjectId(id)}, {"$set": parameters})
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
async def get_guests_from_owner(ownerName: str):
    ownerName = re.compile(".*" + ownerName + ".*", re.IGNORECASE) # type: ignore

    houses_ids = houses.find({"ownerName": {"$regex": ownerName}}, {"_id": 1})
    houses_ids = [{"houseId": str(house_id.get("_id"))} for house_id in houses_ids]
    
    return list(bookings.distinct("guestName", {"$or": houses_ids}))