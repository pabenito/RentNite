# Import libraries
from fastapi import APIRouter, Response
from database import db as db
from bson.objectid import ObjectId
from datetime import datetime, date, time
import re

# Create router
router = APIRouter()

# Initialize DB
users = db["users"]

# API
@router.get("/")
async def root():
    return {"message": "Welcome to users microservice"}

@router.post("/")
async def create(response: Response, username: str, email: str):
    users.insert_one({"username": username, "email": email})
    response.status_code = 201

@router.put("/{id}")
async def update(response: Response,id: str, username: str | None = None, email: str | None = None):
    data = {"username": username, "email": email}
    data = {k: v for k, v in data.items() if v is not None}
    
    if len(data) == 0:
        response.status_code = 400
        return

    try:
        user = users.find_one({"_id": ObjectId(id)})
        
        user = users.find_one_and_update(
            {"_id": ObjectId(id)}, {"$set": data})
    except:
        user = None

    if user is None:
        response.status_code = 404

@router.get("/{id}")
async def get_by_id(response: Response, id: str):
    try:
        user = users.find_one({"_id": ObjectId(id)}, {"_id": 0})
    except:
        user = None

    if user is None:
        response.status_code = 404
    else:
        return user

