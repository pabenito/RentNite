#Import libraries
from fastapi import APIRouter, Query, status, HTTPException
from fastapi.encoders import jsonable_encoder
from pymongo.collection import Collection
from pymongo.results import InsertOneResult
from datetime import datetime, date, time
from pytz import timezone
from app.database import db
from .models import *

#Create router
router = APIRouter()

#Initialize DB
ratings: Collection = db["ratings"]
users: Collection = db["users"]
houses: Collection = db["houses"]

#API
@router.get("/")
def get(
    rater_id: str | None = None,
    rated_user_id: str | None = None,
    rated_user_Name: str | None = None,
    rated_house_id: str | None = None,
    rate: int | None = None,
    from_: date | None = None,
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
        
    if rater_id:
        result = []
        for rated in rate_list:
            rated: Rating  
            if rated.rater_id == rater_id:
                result.append(rated)
        rate_list = result
        
    if rated_user_Name:
        result = []
        for rated in rate_list:
            rated: Rating  
            if rated.rated_user_Name == rated_user_Name:
                result.append(rated)
        rate_list = result

    if rated_user_id:
        result = []
        for rated in rate_list:
            rated: Rating  
            if rated.rated_user_id == rated_user_id:
                result.append(rated)
        rate_list = result
    
    if rated_house_id:
        result = []
        for rated in rate_list:
            rated: Rating  
            if rated.rated_house_id == rated_house_id:
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
            if rated.date.timestamp() <= datetime.combine(to, time.min).timestamp():
                result.append(rated)
        rate_list = result


    result = []
    for rate in rate_list:
        rate: Rating 
        result.append(rate.to_response())
    rate_list = result
    
    return rate_list

@router.post("/", status_code=status.HTTP_201_CREATED)
def create(
    rater_id: str | None = Query(default=None, alias="rater-id"),
    rated_user_id: str | None = Query(default=None, alias="rated-user-id"),
    rated_house_id: str | None = Query(default=None, alias="rated-house-id"),
    rate: int | None = Query(default=None, alias="rate")
    ):
    
    if not rated_user_id and not rated_house_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Ratings needs a rated_user_id or a rated_house_id.")
    if rated_user_id and rated_house_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Ratings needs a rated_user_id or a rated_house_id, but not both.")
    
    new_rate: RatingConstructor = RatingConstructor()
    
    if rated_user_id:
        try:
            user: User = User.parse_obj(users.find_one({"_id": ObjectId(rated_user_id)}))
            new_rate.rated_user_id = str(user.id)
            
        except Exception:  
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"There is no user with that id: {rated_user_id}.")

    if rated_house_id:
        try:
            house: House = House.parse_obj(houses.find_one({"_id": ObjectId(rated_house_id)}))
            new_rate.rated_house_id= str(house.id)
        except Exception: 
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"There is no house with that id: {rated_house_id} .")
    
    if rate:
        if(not(rate>=0 and rate<=5)):
            raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Sorry, no numbers below zero (0) or above five (5): {rate}.")
        else:
            new_rate.rate = rate
    
    new_rate.date = datetime.now(timezone("Europe/Madrid"))
    new_rate.rater_id=rater_id
    userA: User = User.parse_obj(users.find_one({"_id": ObjectId(rater_id)}))
    new_rate.rated_user_Name=str(userA.username)

    inserted_rate: InsertOneResult = ratings.insert_one(jsonable_encoder(new_rate.exclude_unset()))
    created_rate: Rating = Rating.parse_obj(ratings.find_one({"_id": ObjectId(inserted_rate.inserted_id)}))

    return created_rate.to_response()    
    
        
@router.get("/{id}")
def get_by_id(id: str):
    try:
        return Rating.parse_obj(ratings.find_one({"_id": ObjectId(id)})).to_response
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"There is no rating with that id: {id}.")
    


@router.delete("/{id}")
def delete(id: str):
    try:
        rated : Rating = Rating.parse_obj(ratings.find_one_and_delete({"_id": ObjectId(id)}))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"There is no rating with that id: {id}.")

    if not rated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"There is no rating with that id: {id}.")

    return rated.to_response()