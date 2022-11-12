# Import libraries
from fastapi import APIRouter, Response
from app.database import db as db
from bson.objectid import ObjectId
from datetime import datetime, date, time
import re

# Create router
router = APIRouter()

# Initialize DB
users = db["users"]
houses = db["houses"]
bookings = db["bookings"]

# API
@router.get("/")
async def root():
    return {"message": "Welcome to users microservice"}

#Inserta un usuario en la base de datos
@router.post("/")
async def create(response: Response, username: str, email: str):
    users.insert_one({"username": username, "email": email})
    response.status_code = 201

#Actualiza un usuario 
@router.put("/{id}")
async def update(response: Response,id: str, username: str | None = None, email: str | None = None):
    data = {"username": username, "email": email}
    data = {k: v for k, v in data.items() if v is not None}
    
    if len(data) == 0:
        response.status_code = 400
        return

    try: 
        user = users.find_one_and_update(
            {"_id": ObjectId(id)}, {"$set": data})
    except:
        user = None

    if user is None:
        response.status_code = 404

#Devuelve un usuario por su id
@router.get("/{id}")
async def get_by_id(response: Response, id: str):
    try:
        user = users.find_one({"_id": ObjectId(id)}, {"_id": 0})
    except Exception:
        user = None

    if user is None:
        response.status_code = 404
    else:
        return user

#Borra un usuario
@router.delete("/{id}")
async def get_by_id(response: Response, id: str):
    try:
        user = users.find_one_and_delete({"_id": ObjectId(id)})
    except Exception:
        user = None

    if user is None:
        response.status_code = 404

#Devuelve la lista de casas de un usuario
@router.get("/{user_id}/houses")
async def get_houses_from_user(response: Response, user_id: str):
    try:
        user = users.find_one({"_id": ObjectId(user_id)}, {"_id": 0})
    except Exception:
        user = None

    if user is None:
        response.status_code = 404
    else:
        try:
            username = user.get("username")
            username = re.compile(".*" + username + ".*", re.IGNORECASE)
            params = dict()
            params['ownerName'] = user.get("username")
            return list(houses.find(filter=params, projection={"_id": 0}))
        except:
            response.status_code = 404

#Devuelve la lista de reservas de un usuario
@router.get("/{user_id}/bookings")
async def get_bookings_from_user(response: Response, user_id: str):
    try:
        params = dict()
        params['guestId'] = user_id
        return list(bookings.find(filter=params, projection={"_id": 0}))
    except:
        response.status_code = 404     