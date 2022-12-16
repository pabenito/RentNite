# Import libraries
import re
from fastapi.encoders import jsonable_encoder
from fastapi import APIRouter, HTTPException, status
from pymongo.collection import Collection
from pymongo.results import InsertOneResult
from app.database import db
from .models import *
from ..opendata import osm

# Create router
router = APIRouter()

# Initialize DB
houses: Collection = db["houses"]
bookings: Collection = db["bookings"]
users: Collection = db["users"]

# API
@router.get("/")
def get(city: Union[str, None] = None, street: Union[str, None] = None, number: Union[int, None] = None, capacity: Union[int, None] = None, price: Union[float, None] = None, 
        rooms: Union[int, None] = None, bathrooms: Union[int, None] = None, owner_id: Union[str, None] = None, owner_name: Union[str, None] = None, image: Union[str, None] = None, 
        latitude: Union[float, None] = None, longitude: Union[float, None] = None, offset: int = 0, size: int = 0):
    if offset < 0 or size < 0:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid offset or size.")

    filter = {"capacity": capacity, "price": price, "rooms": rooms, "bathrooms": bathrooms,
              "owner_id": owner_id, "image": image, "latitude": latitude, "longitude": longitude}
    filter = {k: v for k, v in filter.items() if v is not None}
    
    if city is not None:
        filter["address"]["city"] = {"$regex": re.compile(".*" + city + ".*", re.IGNORECASE)}

    if street is not None:
        filter["address"]["street"] = {"$regex": re.compile(".*" + street + ".*", re.IGNORECASE)}

    if number is not None:
        filter["address"]["number"] = number

    if owner_name is not None:
        filter["owner_name"] = {"$regex": re.compile(".*" + owner_name + ".*", re.IGNORECASE)}

    if size == 0:
        result: list = list(houses.find(filter, skip = offset))
    else:
        result: list = list(houses.find(filter, skip = offset, limit = size))
    
    return [House.parse_obj(house).to_response() for house in result]


@router.get("/{id}")
def get_by_id(id: str):
    try:
        house = House.parse_obj(houses.find_one({"_id": ObjectId(id)})).to_response()
    except:
        house = None

    if house is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "House not found.")

    return house


@router.post("/", status_code=status.HTTP_201_CREATED)
def create(house: HousePost):
    if house.capacity <= 0 or house.price <= 0 or house.rooms <= 0 or house.bathrooms <= 0:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid parameters.")

    try:
        owner = users.find_one({"_id": ObjectId(house.owner_id)}, {"_id": 0, "username": 1})
    except:
        owner = None

    if owner is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No user was found with the given ID.")

    parameters = jsonable_encoder(house)
    parameters["owner_name"] = owner["username"]

    location = osm.geocode(house.address.city, house.address.street, house.address.number)

    if location is not None:
        parameters["address"]["latitude"] = float(location["lat"])
        parameters["address"]["longitude"] = float(location["lon"])

    inserted_house: InsertOneResult = houses.insert_one(parameters)
    return House.parse_obj(houses.find_one({"_id": ObjectId(inserted_house.inserted_id)})).to_response()


@router.put("/{id}")
def update(id: str, house: HouseConstructor):
    if house.capacity is not None and house.capacity <= 0 or house.price is not None and house.price <= 0 or house.rooms is not None and house.rooms <= 0 or house.bathrooms is not None and house.bathrooms <= 0:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid parameters.")

    parameters = house.exclude_unset()

    if house.address is not None:
        if house.address.city is not None:
            parameters["address"]["city"] = house.address.city
        if house.address.street is not None:
            parameters["address"]["street"] = house.address.street
        if house.address.number is not None:
            parameters["address"]["number"] = house.address.number

        location = osm.geocode(parameters["address"]["city"], parameters["address"]["street"], parameters["address"]["number"])

        if location is not None:
            parameters["address"]["latitude"] = float(location["lat"])
            parameters["address"]["longitude"] = float(location["lon"])

    try:
        result = houses.find_one_and_update({"_id": ObjectId(id)}, {"$set": parameters})
    except:
        result = None

    if result is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "House not found.")


@router.delete("/{id}")
def delete(id: str):
    try:
        house = houses.find_one_and_delete({"_id": ObjectId(id)})
    except:
        house = None

    if house is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "House not found.")

    return house


@router.get("/owner/{owner_name}/guests")
def get_guests_by_owner_name(owner_name: str):
    owner_name = re.compile(".*" + owner_name + ".*", re.IGNORECASE)  # type: ignore

    houses_ids = list(houses.find({"owner_name": {"$regex": owner_name}}, {"_id": 1}))

    if len(houses_ids) == 0:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Owner name not found.")

    houses_ids = [{"house_id": str(house_id.get("_id"))} for house_id in houses_ids]
    
    return bookings.distinct("guest_name", {"$or": houses_ids})
