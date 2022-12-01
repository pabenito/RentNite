# Import libraries
from fastapi import APIRouter, Response, HTTPException, status, Query, File, UploadFile
from app.database import db as db
from bson.objectid import ObjectId
from datetime import datetime, date, time
import re
from passlib.hash import bcrypt
from .models import *


# Create router
router = APIRouter()

# Initialize DB
users = db["users"]
houses = db["houses"]
bookings = db["bookings"]

# API


# Inserta un usuario en la base de datos


@router.post("/")
def create(response: Response, username: str, email: str, password: str):
    # salida = bcrypt.hash(password)
    users.insert_one(
        {"username": username, "email": email, "password_hash": password})
    response.status_code = 201

# Actualiza un usuario


@router.put("/{id}")
def update(id: str, username: str | None = None, email: str | None = None,  password: str | None = None, photo: str | None = None):
    data = {"username": username, "email": email, "password": password, "photo": photo}
    data = {k: v for k, v in data.items() if v is not None}

    if len(data) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Datos no introducidos.")

    try:
        user = users.find_one_and_update(
            {"_id": ObjectId(id)}, {"$set": data})
    except:
        user = None

    

# Devuelve un usuario por su id


@router.get("/{id}")
def get_by_id(id: str):
    try:
        user = users.find_one({"_id": ObjectId(id)}, {"_id": 0})
    except Exception:
        user = None

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User doesnt exists.")
    else:
        return user


@router.get("/")
def general_get(username: str | None = Query(default=None, alias="username"),
                email: str | None = Query(default=None, alias="email")):

    user_list: list = list(users.find())
    result: list = []

    for user_dic in user_list:
        result.append(User.parse_obj(user_dic))

    user_list = result

    if username:
        result = []
        for user in user_list:
            user: User
            if user.username == username:
                result.append(user)
        user_list = result

    if email:
        result = []
        for user in user_list:
            user: User
            if user.email == email:
                result.append(user)
        user_list = result

    result = []
    for user in user_list:
        user: User
        result.append(user.to_response())
    user_list = result

    return user_list


# @router.get("/")
# def login_get(username: str | None = Query(default=None, alias="username"),
#                 email: str | None = Query(default=None, alias="email"),
#     ):

#     filter = {"username": username, "email": email}
#     filter = {k: v for k, v in filter.items() if v is not None}


#     if username is not None:
#         filter["username"] = {"$regex": re.compile(
#             ".*" + username + ".*", re.IGNORECASE)}

#     if email is not None:
#         filter["owner_name"] = {"$regex": re.compile(
#             ".*" + email + ".*", re.IGNORECASE)}
    
#     result = (houses.find_one(filter))
    
#     return result


# Borra un usuario

@router.delete("/{id}")
def delete(response: Response, id: str):
    try:
        user = users.find_one_and_delete({"_id": ObjectId(id)})
    except Exception:
        user = None

    if user is None:
        response.status_code = 404

# Devuelve la lista de casas de un usuario


@router.get("/{user_id}/houses")
def get_houses_from_user(response: Response, user_id: str):
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

# Devuelve la lista de reservas de un usuario


@router.get("/{user_id}/bookings")
def get_bookings_from_user(response: Response, user_id: str):
    try:
        params = dict()
        params['guestId'] = user_id
        return list(bookings.find(filter=params, projection={"_id": 0}))
    except:
        response.status_code = 404
