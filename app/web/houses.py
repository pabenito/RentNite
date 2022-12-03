from fastapi import APIRouter, Request, Cookie, Form, HTTPException, File, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from ..entities.models import *
from . import login as login_api
from ..entities import houses as houses_api
from ..entities import messages as messages_api
from ..entities import ratings as ratings_api
from datetime import date, datetime, timedelta
from ..opendata import aemet as aemet_api
import cloudinary.uploader

router = APIRouter()

templates = Jinja2Templates(directory="templates")

DEFAULT_IMAGE = "http://res.cloudinary.com/dc4yqjivf/image/upload/v1670022360/amv2l4auluxikphjsc0w.png"

@router.get("/", response_class = HTMLResponse)
def read_item(request: Request):
    user_id = __chechUser()

    return templates.TemplateResponse("offeredHouses.html", {"request": request, "houses": houses_api.get()})

@router.get("/myHouses", response_class = HTMLResponse)
def my_houses(request: Request):
    user_id = __chechUser()

    return templates.TemplateResponse("myHouses.html", {"request": request, "houses": houses_api.get(owner_id = user_id)})

@router.get("/create", response_class = HTMLResponse)
def create_house(request: Request):
    user_id = __chechUser()

    address: AddressPost = AddressPost(city = "", street = "", number = 1)

    

    house: HousePost = HousePost(address = address, capacity = 1, price = 0, rooms = 1, bathrooms = 1, owner_id = user_id,
                                 image = DEFAULT_IMAGE)

    return __loadHouseDetails(request, house, True, False, "", "", None, None, None, None, None, None, user_id)

@router.post("/save", response_class = HTMLResponse)
def update_house(request: Request, id: str = Form(), city: str = Form(), street: str = Form(), number: int = Form(), capacity: int = Form(), 
                 price: str = Form(), rooms: int = Form(), bathrooms: int = Form(), file: UploadFile = File()):
    user_id = __chechUser()
    
    try:
        price_float: float = float(price)

        if file.filename == "":
            url = DEFAULT_IMAGE
        else:
            # Upload photo to Cloudinary
            result = cloudinary.uploader.upload(file.file)
            url = result.get("url")

        if id == "None":
            address = AddressPost(city = city, street = street, number = number)

            house = HousePost(address = address, capacity = capacity, price = price_float, rooms = rooms, bathrooms = bathrooms, owner_id = user_id, 
                              image = url)
            house = houses_api.create(house)
            id = house["id"]
        else:
            house = houses_api.get_by_id(id)

            # Take photo's URL and get name of file to delete
            name =  house["image"].split("/")
            name =  name[7]
            size = len(name)
            name = name[:size-4]

            # Delete photo from Cloudinary
            cloudinary.uploader.destroy(name)

            address = AddressConstructor(city = city, street = street, number = number)

            house = HouseConstructor(address = address, capacity = capacity, price = price_float, rooms = rooms, bathrooms = bathrooms, image = url)
            houses_api.update(id, house)

        return my_houses(request)
    except:
        return edit_house(request, id, "Los valores introducidos no son validos")

@router.get("/{id}", response_class = HTMLResponse)
def house_details(request: Request, id: str, booking_error: str = ""):
    user_id = __chechUser()

    house: dict = houses_api.get_by_id(id)

    latitude = house["address"].get("latitude")
    longitude = house["address"].get("longitude")
    
    try:
        weather: dict = aemet_api.get_forecast_precipitation_daily(latitude = latitude, longitude = longitude)
        temperature: dict = aemet_api.get_forecast_temperature_daily(latitude = latitude, longitude = longitude)
    except:
        weather: dict = dict()
        temperature: dict = dict()

    comments: list = messages_api.get(None, id, None, None, None)
    ratings: list = ratings_api.get(None,None,None,id,None,None,None)
    today: date = date.today()
    tomorrow: date = today + timedelta(1)

    return __loadHouseDetails(request, house, False, False, "", booking_error, comments, ratings, today, tomorrow, weather, temperature, user_id)

@router.get("/{id}/edit", response_class = HTMLResponse)
def edit_house(request: Request, id: str, error: str = ""):
    user_id = __chechUser()

    house: dict = houses_api.get_by_id(id)

    return __loadHouseDetails(request, house, False, True, error, "", None, None, None, None, None, None, user_id)

@router.get("/{id}/delete", response_class = HTMLResponse)
def delete_house(request: Request, id: str):
    user_id = __chechUser()

    houses_api.delete(id)

    return my_houses(request)

@router.post("/{id}/addComment", response_class = HTMLResponse)
def add_comment(request: Request, id: str, comment: str = Form(title="coment")):
    user_id = __chechUser()

    message: MessagePost = MessagePost(sender_id=user_id, message=comment, house_id=id)
    messages_api.post(message)

    return house_details(request, id)

@router.get("/{id}/deleteComment/{comment_id}", response_class = HTMLResponse)
def delete_comment(request: Request, id: str, comment_id: str):
    messages_api.delete(comment_id)

    return house_details(request, id)
    
@router.post("/{id}/addRate", response_class=HTMLResponse)
def add_rate(request: Request, id: str, estrellas: int = Form()):
    user_id = __chechUser()

    ratings_api.create(user_id, None, id, estrellas)

    return house_details(request, id) 

# Private methods

def __loadHouseDetails(request: Request, house: HousePost | dict, creating: bool, editing: bool, error: str, booking_error: str, comments: list | None, 
                       ratings: list | None, today_date: date | None, tomorrow_date: date | None, weather: dict | None, temperature: dict | None, 
                       user_id: str):
    return templates.TemplateResponse("houseDetails.html", {"request": request, "house": house, "creating": creating, "editing": editing, 
                                                            "error": error, "booking_error": booking_error, "comments": comments, "ratings": ratings, 
                                                            "today_date": today_date, "tomorrow_date": tomorrow_date, "weather": weather, 
                                                            "temperature": temperature, "user_id": user_id})

def __chechUser():
    session = login_api.Singleton()
    if session.user is None:
        raise HTTPException(
            status_code=401, detail="No se ha iniciado sesión.")
    return session.user