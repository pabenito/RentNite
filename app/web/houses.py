from typing import Union
from fastapi import APIRouter, Request, Form, File, UploadFile, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from ..entities.models import *
from . import login
from ..entities import houses as houses_api
from ..entities import bookings as bookings_api
from ..entities import messages as messages_api
from ..entities import ratings as ratings_api
from datetime import date, datetime, timedelta
from ..opendata import aemet as aemet_api
from .. import cloudinary as cloud
from ..payments import get_token
from app.entities import models
from pytz import timezone

router = APIRouter()

templates = Jinja2Templates(directory = "templates")

@router.get("/", response_class = HTMLResponse)
def read_item(request: Request, user_id: Union[str, None] = Cookie(default=None)):
    return templates.TemplateResponse("offeredHouses.html", {"request": request, "houses": houses_api.get(), "user_id": str(user_id)})

@router.get("/myHouses", response_class = HTMLResponse)
def my_houses(request: Request, user_id: Union[str, None] = Cookie(default=None)):
    if user_id is None:
        return RedirectResponse("/login")    

    return templates.TemplateResponse("myHouses.html", {"request": request, "houses": houses_api.get(owner_id = str(user_id)), "user_id": str(user_id)})

@router.get("/create", response_class = HTMLResponse)
def create_house(request: Request, user_id: Union[str, None] = Cookie(default=None)):
    if user_id is None:
        return RedirectResponse("/login")

    house: dict = {"address": {"city": "", "street": "", "number": 1}, "capacity": 1, "price": 0.01, "rooms": 1, "bathrooms": 1, "owner_id": str(user_id)}
    return __load_house_details(request, house, str(user_id), creating = True)

@router.post("/save", response_class = HTMLResponse)
def update_house(request: Request, id: str = Form(), city: str = Form(), street: str = Form(), number: int = Form(), capacity: int = Form(), 
                 price: float = Form(), rooms: int = Form(), bathrooms: int = Form(), file: UploadFile = File(), user_id: Union[str, None] = Cookie(default=None)):
    if user_id is None:
        return RedirectResponse("/login")

    if id == "None":
        address = AddressPost(city = city, street = street, number = number)
        house = HousePost(address = address, capacity = capacity, price = price, rooms = rooms, bathrooms = bathrooms, owner_id = str(user_id))

        if file.filename != "":
            house.image = cloud.upload_photo_house(file = file)

        house = houses_api.create(house)
        id = house["id"]
    else:
        house_db = houses_api.get_by_id(id)

        address = AddressConstructor(city = city, street = street, number = number)
        house = HouseConstructor(address = address, capacity = capacity, price = price, rooms = rooms, bathrooms = bathrooms)

        if file.filename != "":
            house.image = cloud.upload_photo_house(file = file)

            if house_db.get("image") is not None:
                photo_id = cloud.get_photo_id(url = house_db["image"])
                cloud.delete_photo(name = photo_id)

        houses_api.update(id, house)

    return my_houses(request, user_id)

@router.get("/{id}", response_class = HTMLResponse)
def house_details(request: Request, id: str, booking_error: str = "", user_id: Union[str, None] = Cookie(default=None)):
    house: dict = houses_api.get_by_id(id)

    latitude = house["address"].get("latitude")
    longitude = house["address"].get("longitude")
    
    try:
        weather: dict = aemet_api.get_forecast_precipitation_daily(latitude = latitude, longitude = longitude)
        temperature: dict = aemet_api.get_forecast_temperature_daily(latitude = latitude, longitude = longitude)
    except:
        weather: dict = dict()
        temperature: dict = dict()

    comments: list = messages_api.get(house_id = id)
    ratings: list = ratings_api.get(rated_house_id = id)
    today: date = date.today()
    tomorrow: date = today + timedelta(1)

    return __load_house_details(request, house, str(user_id), error = booking_error, comments = comments, ratings = ratings, weather = weather, 
                                temperature = temperature)

@router.get("/{id}/edit", response_class = HTMLResponse)
def edit_house(request: Request, id: str, error: str = "", user_id: Union[str, None] = Cookie(default=None)):
    if user_id is None:
        return RedirectResponse("/login")

    house: dict = houses_api.get_by_id(id)

    return __load_house_details(request, house, str(user_id), editing = True, error = error)

@router.get("/{id}/delete", response_class = HTMLResponse)
def delete_house(request: Request, id: str, user_id: Union[str, None] = Cookie(default=None)):
    if user_id is None:
        return RedirectResponse("/login")

    house: dict = houses_api.delete(id)

    if house.get("image") is not None:
        photo_id = cloud.get_photo_id(url = house["image"])
        cloud.delete_photo(name = photo_id)

    return my_houses(request, user_id)

@router.post("/{id}/addComment", response_class = HTMLResponse)
def add_comment(request: Request, id: str, comment: str = Form(title="coment"), user_id: Union[str, None] = Cookie(default=None)):
    if user_id is None:
        return RedirectResponse("/login")

    message: MessagePost = MessagePost(sender_id=str(user_id), message=comment, house_id=id)
    messages_api.post(message)

    return house_details(request, id)

@router.get("/{id}/deleteComment/{comment_id}", response_class = HTMLResponse)
def delete_comment(request: Request, id: str, comment_id: str, user_id: Union[str, None] = Cookie(default=None)):
    if user_id is None:
        RedirectResponse("/login")

    messages_api.delete(comment_id)

    return house_details(request, id)
    
@router.post("/{id}/addRating", response_class=HTMLResponse)
def add_rating(request: Request, id: str, estrellas: int = Form(), comment: str = Form(), user_id: Union[str, None] = Cookie(default=None)):
    if user_id is None:
        return RedirectResponse("/login")

    date = datetime.now(timezone("Europe/Madrid"))
    rt : RatingPost = RatingPost(rater_id=str(user_id) ,date=date,rated_user_id=None,
                                               rated_user_Name=None,rated_house_id=id,rate=estrellas,comment=comment)
    ratings_api.create(rt)

    return house_details(request, id) 

@router.get("/{id}/deleteRating/{rating_id}", response_class = HTMLResponse)
def delete_rating(request: Request, id: str, rating_id: str, user_id: Union[str, None] = Cookie(default=None)):
    if user_id is None:
        return RedirectResponse("/login")

    ratings_api.delete(rating_id)

    return house_details(request, id)

# Private methods

def __load_house_details(request: Request, house: dict, user_id: Union[str, None], creating: bool = False, editing: bool = False, 
                         error: str = "", comments: Union[list, None] = None, ratings: Union[list, None] = None, weather: Union[dict, None] = None,
                         temperature: Union[dict, None] = None):
    if creating or editing:
        today = tomorrow = None
        user_can_rate = False
    else:
        today = date.today()
        tomorrow = today + timedelta(1)
        user_can_rate = __user_can_rate(user_id, house)

    payment_token = get_token(user_id)
    
    return templates.TemplateResponse("houseDetails.html", {"request": request, "house": house, "user_id": user_id, "creating": creating, 
                                                            "editing": editing, "error": error, "comments": comments, "ratings": ratings, 
                                                            "weather": weather, "temperature": temperature, "today_date": today,
                                                            "tomorrow_date": tomorrow, "user_can_rate": user_can_rate,
                                                            "payment_token": payment_token})


def __user_can_rate(user_id: Union[str, None], house: dict):
    if user_id is None:
        return True

    user_can_rate = False

    if user_id != house["owner_id"]:
            user_bookings = bookings_api.search(guest_id = user_id, house_id = house["id"])
            if len(user_bookings) > 0:
                user_ratings = ratings_api.get(rater_id = user_id, rated_house_id = house["id"])
                if len(user_ratings) == 0:
                    user_can_rate = True
    
    return user_can_rate