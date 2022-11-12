# Import libraries
from fastapi import APIRouter, HTTPException, status
from app.database import db as db
from bson.objectid import ObjectId
import re

# Create router
router = APIRouter()

# Initialize DB
houses = db["houses"]
bookings = db["bookings"]

# API
@router.get("/")
async def root():
    return {"message": "Welcome to houses microservice"}

@router.post("/", status_code = status.HTTP_201_CREATED)
async def create(address: str, capacity: int, price: float, rooms: int, bathrooms: int, ownerName: str):
    if capacity <= 0 or price < 0 or rooms <= 0 or bathrooms <= 0 or not re.fullmatch("[a-zA-Z]+( [a-zA-Z]+)*", ownerName):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Parametros no validos.")
    
    houses.insert_one({"address": address, "capacity": capacity, "price": price, 
                       "rooms": rooms, "bathrooms": bathrooms, "ownerName": ownerName})

@router.get("/{id}")
async def get_by_id(id: str):
    try:
        house = houses.find_one({"_id": ObjectId(id)}, {"_id": 0})
    except:
        house = None

    if house is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Casa no encontrada.")

    return house

@router.get("/range/")
async def get_range(size: int, offset: int = 0):
    if offset < 0 or size <= 0:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Parametros no validos.")
    
    return list(houses.find(projection = {"_id": 0}, skip = offset, limit = size))

@router.get("/address/{address}")
async def get_by_address(address: str):
    address = re.compile(".*" + address + ".*", re.IGNORECASE) # type: ignore
    return list(houses.find({"address": {"$regex": address}}, {"_id": 0}))

@router.put("/{id}")
async def update(id: str, address: str | None = None, capacity: int | None = None, 
                 price: int | None = None, rooms: int | None = None, bathrooms: int | None = None):
    data = {"address": address, "capacity": capacity, "price": price, "rooms": rooms, "bathrooms": bathrooms}
    data = {k: v for k, v in data.items() if v is not None}

    if len(data) == 0:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "No se ha proporcionado ningun dato para actualizar.")

    if ((capacity or 1) <= 0) or ((price or 1) < 0) or ((rooms or 1) <= 0) or ((bathrooms or 1) <= 0):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Parametros no validos.")

    try:
        house = houses.find_one_and_update({"_id": ObjectId(id)}, {"$set": data})
    except:
        house = None

    if house is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Casa no encontrada.")

@router.delete("/{id}")
async def delete(id: str):
    try:
        house = houses.find_one_and_delete({"_id": ObjectId(id)})
    except:
        house = None
    
    if house is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Casa no encontrada.")

@router.get("/owner/{ownerName}/guests")
async def get_guests_from_owners(ownerName: str):
    ownerName = re.compile(".*" + ownerName + ".*", re.IGNORECASE) # type: ignore

    houses_ids = houses.find({"ownerName": {"$regex": ownerName}}, {"_id": 1})
    houses_ids = [{"houseId": str(house_id.get("_id"))} for house_id in houses_ids]
    
    return list(bookings.distinct("guestName", {"$or": houses_ids}))