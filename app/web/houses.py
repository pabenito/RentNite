from fastapi import APIRouter, Request, Cookie, Form, HTTPException, File, UploadFile
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
from app.entities import models
from pytz import timezone


router = APIRouter()

templates = Jinja2Templates(directory="templates")

DEFAULT_IMAGE = "http://res.cloudinary.com/dc4yqjivf/image/upload/v1670022360/amv2l4auluxikphjsc0w.png"

@router.get("/", response_class = HTMLResponse)
def read_item(request: Request):
    login.check_user()

    return templates.TemplateResponse("offeredHouses.html", {"request": request, "houses": houses_api.get(), "default_image": DEFAULT_IMAGE})

@router.get("/myHouses", response_class = HTMLResponse)
def my_houses(request: Request):
    user_id = login.check_user()

    return templates.TemplateResponse("myHouses.html", {"request": request, "houses": houses_api.get(owner_id = user_id), "default_image": DEFAULT_IMAGE})

@router.get("/create", response_class = HTMLResponse)
def create_house(request: Request):
    user_id = login.check_user()

    house: dict = {"address": {"city": "", "street": "", "number": 1}, "capacity": 1, "price": 0.01, "rooms": 1, "bathrooms": 1, "owner_id": user_id, 
                   "image": DEFAULT_IMAGE}
    return __load_house_details(request, house, user_id, creating = True)

@router.post("/save", response_class = HTMLResponse)
def update_house(request: Request, id: str = Form(), city: str = Form(), street: str = Form(), number: int = Form(), capacity: int = Form(), 
                 price: float = Form(), rooms: int = Form(), bathrooms: int = Form(), file: UploadFile = File()):
    user_id = login.check_user()
    
    if file.filename != "":
        # Upload photo to Cloudinary
        url = cloud.uploadPhotoHouse(file=file)

    if id == "None":
        if file.filename == "":
            url = ""

        address = AddressPost(city = city, street = street, number = number)

        house = HousePost(address = address, capacity = capacity, price = price, rooms = rooms, bathrooms = bathrooms, owner_id = user_id, 
                            image = url)
        house = houses_api.create(house)
        id = house["id"]
    else:
        house = houses_api.get_by_id(id)

        if file.filename == "":
            url = house["image"]
        elif house["image"] != "":
            name_photo = cloud.getPhotoId(url=house["image"])
            cloud.deletePhoto(name=name_photo)

        address = AddressConstructor(city = city, street = street, number = number)

        house = HouseConstructor(address = address, capacity = capacity, price = price, rooms = rooms, bathrooms = bathrooms, image = url)
        houses_api.update(id, house)

    return my_houses(request)

@router.get("/{id}", response_class = HTMLResponse)
def house_details(request: Request, id: str, booking_error: str = ""):
    user_id = login.check_user()

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

    return __load_house_details(request, house, user_id, error = booking_error, comments = comments, ratings = ratings, weather = weather, 
                                temperature = temperature)

@router.get("/{id}/edit", response_class = HTMLResponse)
def edit_house(request: Request, id: str, error: str = ""):
    user_id = login.check_user()

    house: dict = houses_api.get_by_id(id)

    return __load_house_details(request, house, user_id, editing = True, error = error)

@router.get("/{id}/delete", response_class = HTMLResponse)
def delete_house(request: Request, id: str):
    login.check_user()

    house: dict = houses_api.delete(id)

    if house["image"] != "":
        name_photo = cloud.getPhotoId(url=house["image"])
        cloud.deletePhoto(name=name_photo)

    return my_houses(request)

@router.post("/{id}/addComment", response_class = HTMLResponse)
def add_comment(request: Request, id: str, comment: str = Form(title="coment")):
    user_id = login.check_user()

    message: MessagePost = MessagePost(sender_id=user_id, message=comment, house_id=id)
    messages_api.post(message)

    return house_details(request, id)

@router.get("/{id}/deleteComment/{comment_id}", response_class = HTMLResponse)
def delete_comment(request: Request, id: str, comment_id: str):
    login.check_user()

    messages_api.delete(comment_id)

    return house_details(request, id)
    
@router.post("/{id}/addRating", response_class=HTMLResponse)
def add_rating(request: Request, id: str, estrellas: int = Form(), comment: str = Form()):
    user_id = login.check_user()

    date = datetime.now(timezone("Europe/Madrid"))
    rt : models.RatingPost = models.RatingPost(rater_id=user_id ,date=date,rated_user_id=None,
                                               ratd_user_Name=None,rated_house_id=id,rate=estrellas,comment=comment)
    ratings_api.create(rt)

    return house_details(request, id) 

@router.get("/{id}/deleteRating/{rating_id}", response_class = HTMLResponse)
def delete_rating(request: Request, id: str, rating_id: str):
    login.check_user()

    ratings_api.delete(rating_id)

    return house_details(request, id)

# Private methods

def __load_house_details(request: Request, house: dict, user_id: str, creating: bool = False, editing: bool = False, error: str = "", 
                         comments: list | None = None, ratings: list | None = None, weather: dict | None = None, temperature: dict | None = None):
    if creating or editing:
        today = tomorrow = None
        user_can_rate = False
    else:
        today = date.today()
        tomorrow = today + timedelta(1)
        user_can_rate = __user_can_rate(user_id, house)
    
    return templates.TemplateResponse("houseDetails.html", {"request": request, "house": house, "user_id": user_id, "creating": creating, 
                                                            "editing": editing, "error": error, "comments": comments, "ratings": ratings, 
                                                            "weather": weather, "temperature": temperature, "default_image": DEFAULT_IMAGE, 
                                                            "today_date": today, "tomorrow_date": tomorrow, "user_can_rate": user_can_rate})


def __user_can_rate(user_id: str, house: dict):
    user_can_rate = False

    if user_id != house["owner_id"]:
            user_bookings = bookings_api.search(guest_id = user_id, house_id = house["id"])
            if len(user_bookings) > 0:
                user_ratings = ratings_api.get(rater_id = user_id, rated_house_id = house["id"])
                if len(user_ratings) == 0:
                    user_can_rate = True
    
    return user_can_rate