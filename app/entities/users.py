# Import libraries
from fastapi import APIRouter, Response, HTTPException, status, Query, File, UploadFile
from app.database import db as db
from bson.objectid import ObjectId
from datetime import datetime, date, time
import re
from passlib.hash import sha256_crypt
from .models import *
from fastapi.encoders import jsonable_encoder
from pymongo.results import InsertOneResult



# Create router
router = APIRouter()

# Initialize DB
users = db["users"]
houses = db["houses"]
bookings = db["bookings"]

# API


# Inserta un usuario en la base de datos


@router.post("/")
def create(username: str, email: str, password: str):
    users_with_same_email = general_get(email = email)

    if users_with_same_email is not None and len(users_with_same_email) > 0:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "El email ya esta en uso")

    salida = sha256_crypt.hash(password)
    users.insert_one(
        {"username": username, "email": email, "password_hash": salida,"photo":""})
    
@router.post("/")   
def createAUX(username: str, email: str):
    users_with_same_email : User = general_get(email = email)

    if users_with_same_email is not None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "El email ya esta en uso")

    users.insert_one(
        {"username": username, "email": email, "password_hash": "","photo":""})
    
    userAux : User = general_get(email=email)
    return userAux
    

# Actualiza un usuario


@router.put("/{id}")
def update(id: str, username: Union[str, None] = None, email: Union[str, None] = None,  password: Union[str, None] = None, photo: Union[str, None] = None):
    if email is not None:
        users_with_same_email = general_get(email = email)
        length = len(users_with_same_email)

        if length > 1 or (length == 1 and users_with_same_email[0]["id"] != id):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "El email ya esta en uso")

    if password is not None:
        if len(password) < 20:
            data = {"username": username, "email": email, "password_hash": sha256_crypt.hash(password), "photo": photo}
        else:
            data = {"username": username, "email": email, "password_hash": password, "photo": photo}
    else:
        data = {"username": username, "email": email, "password_hash": password, "photo": photo}

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
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.")
    else:
        return user


@router.get("/")
def general_get(username: Union[str, None] = None,
                email: Union[str, None] = None):

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
        email = email.lower()

        result = []
        for user in user_list:
            user: User
            if user.email.lower() == email:
                result.append(user)
        user_list = result

    result = []
    for user in user_list:
        user: User
        result.append(user.to_response())
    user_list = result

    if user_list is not None and len(user_list) > 0:
        user : User = user_list[0]
        return user 
    
    return None


# @router.get("/")
# def login_get(username: Union[str, None] = Query(default=None, alias="username"),
#                 email: Union[str, None] = Query(default=None, alias="email"),
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
