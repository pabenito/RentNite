# Import libraries
from fastapi import APIRouter, Query, status, HTTPException
from fastapi.encoders import jsonable_encoder
from pymongo.collection import Collection
from pymongo.results import InsertOneResult
from datetime import datetime, date, time
from pytz import timezone
from app.database import db as db
from .models import *

# Create router
router = APIRouter()

# Initialize DB
ratings: Collection = db["ratings"]
users: Collection = db["users"]
houses: Collection = db["houses"]

# API
@router.get("/")
async def get(
    rated_user_id: str | None = Query(default=None, alias="user-id"),
    reted_house_id: str | None = Query(default=None, alias="house-id"),
    rate: int | None = Query(default=None, alias="rate"),
    from_: date | None = Query(default=None, alias="from"),
    to: date | None = None
):
    rate_list: list = list(ratings.find())
    result : list = []
    
    for rate_dic in rate_list:
        result.append(Rating.parse_obj(rate_dic))
        
    rate_list = result
    
    if rated_user_id:
        result = []
        for rated in rate_list:
            rated: Rating  
            if rated.rated_user_id == rated_user_id:
                result.append(rated)
        rate_list = result
        
    if reted_house_id:
        result = []
        for rated in rate_list:
            rated: Rating  
            if rated.reted_house_id == reted_house_id:
                result.append(rated)
        rate_list = result
        
    if rate:
        result = []
        for rated in rate_list:
            rated: Rating  
            if rated.rate == rate:
                result.append(rated)
        rate_list = result    
    
    if from_:
        result = []
        for rated in rate_list:
            rated : Rating  
            if rated.date.timestamp() >= datetime.combine(from_, time.min).timestamp():
                result.append(rated)
        rate_list = result

    if to:
        result = []
        for rated in rate_list:
            rated : Rating  
            if rated.date.timestamp() <=datetime.combine(from_, time.min).timestamp():
                result.append(rated)
        rate_list = result
    
    
    result = []
    for rate in rate_list:
        rate: Rating 
        result.append(rate.to_response())
    rate_list = result
    
    return rate_list

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create(
    date_: date, 
    rating: int, 
    user_Id: str, 
    house_Id: str
    ):
    date_ = datetime.combine(date_, time.min)
    if rating >= 0 and rating <= 5:
        ratings.insert_one({"date": date_, "rating": rating, "house_id": house_Id, 
                           "user_id": user_Id})
        response.status_code = 201
    else:
        response.status_code = 400
        
@router.put("/{id}")
async def update(id: str, date_: date | None = None, rating: int | None = None):
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