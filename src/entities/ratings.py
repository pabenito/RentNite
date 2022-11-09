# Import libraries
from fastapi import APIRouter, Response
from database import db as db
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