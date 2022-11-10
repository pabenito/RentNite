# Import libraries
from fastapi import APIRouter, Response
from database import db as db #app.database
from bson.objectid import ObjectId
from datetime import datetime, date, time
import re

# Create router
router = APIRouter()

# Initialize DB
ratings = db["ratings"]

# API
@router.get("/")
async def root():
    return {"message": "Welcome to ratings microservice"}

@router.post("/")
async def create(response: Response, date_: date, rating: int, user_Id: str, house_Id: str):
    date_ = datetime.combine(date_, time.min)
    if rating >= 0 and rating <= 5:
        ratings.insert_one({"date": date_, "rating": rating, "house_id": house_Id, 
                           "user_id": user_Id})
        response.status_code = 201
    else:
        response.status_code = 400
        
@router.put("/{id}")
async def update(response: Response, id: str, date_: date | None = None, rating: int | None = None):
    if date_ is not None:
        date_ = datetime.combine(date_, time.min)
    

    data = {"date": date_, "rating": rating}
    data = {k: v for k, v in data.items() if v is not None}

    if len(data) == 0:
        response.status_code = 400
        return

    if (rating is not None or (rating < 0) or (rating > 5) ):
        response.status_code = 400
        return

    try:
        rating = ratings.find_one_and_update(
            {"_id": ObjectId(id)}, {"$set": data})
    except Exception:
        rating = None

    if rating is None:
        response.status_code = 404
        
@router.get("/{id}")
async def get_by_id(response: Response, id: str):
    try:
        rating = ratings.find_one({"_id": ObjectId(id)}, {"_id": 0})
    except Exception:
        rating = None

    if rating is None:
        response.status_code = 404
    else:
        return rating
    
@router.get("/user/{user_id}")
async def get_by_user_id(user_id: str):
    user_id = re.compile(".*" + user_id + ".*",
                          re.IGNORECASE)  # type: ignore
    return [r for r in ratings.find({"user_id": {"$regex": user_id}}, {"_id": 0})]


@router.delete("/{id}")
async def delete(response: Response, id: str):
    try:
        rating = ratings.find_one_and_delete({"_id": ObjectId(id)})
    except Exception:
        rating = None

    if rating is None:
        response.status_code = 404