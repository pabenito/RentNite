# Import libraries
from fastapi import APIRouter, Response
from app.database import db as db
from bson.objectid import ObjectId
import re

# Create router
router = APIRouter()

# Houses collection
houses = db["houses"]

# API
@router.get("/")
async def root():
    return {"message": "Welcome to houses microservice"}

@router.post("/")
async def create(response: Response, address: str, capacity: int, price: float, rooms: int, bathrooms: int, ownerName: str):
    if capacity > 0 and price >= 0 and rooms > 0 and bathrooms > 0 and re.fullmatch(r"[a-zA-Z ]+", ownerName):
        houses.insert_one({"address": address, "capacity": capacity, "price": price, 
                           "rooms": rooms, "bathrooms": bathrooms, "ownerName": ownerName})
        response.status_code = 201
    else:
        response.status_code = 400

@router.get("/{id}")
async def get_by_id(response: Response, id: str):
    try:
        house = houses.find_one({"_id": ObjectId(id)}, {"_id": 0})
    except:
        house = None

    if house is None:
        response.status_code = 404
    else:
        return house

@router.get("/range/")
async def get_range(response: Response, size: int, offset: int = 0):
    if offset >= 0 and size > 0:
       return [h for h in houses.find(projection = {"_id": 0}, skip = offset, limit = size)]
    else: 
        response.status_code = 400

@router.get("/address/{address}")
async def get_by_address(address: str):
    address = re.compile(".*" + address + ".*", re.IGNORECASE)
    return [h for h in houses.find({"address": {"$regex": address}}, {"_id": 0})]

@router.put("/{id}")
async def update(response: Response, id: str, address: str | None = None, capacity: int | None = None, 
                 price: int | None = None, rooms: int | None = None, bathrooms: int | None = None):
    data = {"address": address, "capacity": capacity, "price": price, "rooms": rooms, "bathrooms": bathrooms}
    data = {k: v for k, v in data.items() if v is not None}

    if len(data) == 0:
        response.status_code = 400
        return

    for k, v in data.items():
        if type(v) is int and (v < 0 or k != "price" and v == 0):
            response.status_code = 400
            return

    try:
        house = houses.find_one_and_update({"_id": ObjectId(id)}, {"$set": data})
    except:
        house = None

    if house is None:
        response.status_code = 404

@router.delete("/{id}")
async def delete(response: Response, id: str):
    try:
        house = houses.find_one_and_delete({"_id": ObjectId(id)})
    except:
        house = None
    
    if house is None:
        response.status_code = 404

@router.get("/owner/{ownerName}/guests")
async def get_guests_from_owners_houses(ownerName: str):
    ownerName = re.compile(".*" + ownerName + ".*", re.IGNORECASE)
    housesIds = [str(h.get("_id")) for h in houses.find({"ownerName": {"$regex": ownerName}})]
    guestsNames = []

    for id in housesIds:
        guestsNames.append({"houseId": id})
    
    return [h for h in db["bookings"].distinct("userName", {"$or": guestsNames})]
