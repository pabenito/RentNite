from fastapi import APIRouter, Request, Cookie, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from ..entities.models import *
from . import login as login_api
from ..entities import houses as houses_api
from ..entities import messages as messages_api
from ..entities import ratings as ratings_api
from datetime import date, datetime, timedelta
from ..opendata import aemet as aemet_api

router = APIRouter()

templates = Jinja2Templates(directory="templates")

@router.get("/", response_class = HTMLResponse)
def read_item(request: Request):
    user_id = __chechUser()
    if user_id == "None":
        return RedirectResponse("/login")

    return templates.TemplateResponse("offeredHouses.html", {"request": request, "houses": houses_api.get()})

@router.get("/myHouses", response_class = HTMLResponse)
def my_houses(request: Request):
    user_id = __chechUser()
    if user_id == "None":
        return RedirectResponse("/login")

    return templates.TemplateResponse("myHouses.html", {"request": request, "houses": houses_api.get(owner_id = user_id)})

@router.get("/create", response_class = HTMLResponse)
def create_house(request: Request):
    user_id = __chechUser()
    if user_id == "None":
        return RedirectResponse("/login")

    house: HousePost = HousePost(address = "", capacity = 1, price = 0, rooms = 1, bathrooms = 1, owner_id = user_id,
                                 image = "https://live.staticflickr.com/65535/52527243603_413f2bc2c3_n.jpg")

    return __loadHouseDetails(request, house, True, False, "", "", None, None, None, None, None, None, user_id)

@router.post("/save", response_class = HTMLResponse)
def update_house(request: Request, id: str = Form(), address: str = Form(), capacity: int = Form(), price: str = Form(), rooms: int = Form(), 
                 bathrooms: int = Form()):
    user_id = __chechUser()
    if user_id == "None":
        return RedirectResponse("/login")
    
    try:
        price_float: float = float(price)

        if id == "None":
            house = HousePost(address = address, capacity = capacity, price = price_float, rooms = rooms, bathrooms = bathrooms, owner_id = user_id, 
                              image = "https://live.staticflickr.com/65535/52527243603_413f2bc2c3_n.jpg")
            house = houses_api.create(house)
            id = house["id"]
        else:
            house = HouseConstructor(address = address, capacity = capacity, price = price_float, rooms = rooms, bathrooms = bathrooms, 
                                     latitude = latitude_float, longitude = longitude_float)
            houses_api.update(id, house)

        return my_houses(request)
    except:
        return edit_house(request, id, "Los valores introducidos no son validos")

@router.get("/{id}", response_class = HTMLResponse)
def house_details(request: Request, id: str, booking_error: str = ""):
    user_id = __chechUser()
    if user_id == "None":
        return RedirectResponse("/login")

    house: dict = houses_api.get_by_id(id)
    comments: list = messages_api.get(None, id, None, None, None)
    ratings: list = ratings_api.get(None,None,None,id,None,None,None)

    tiempo: dict = aemet_api.get_forecast_precipitation_daily(latitude = house["latitude"], longitude = house["longitude"])
    temperatura: dict = aemet_api.get_forecast_temperature_daily(latitude = house["latitude"], longitude = house["longitude"])
    today: date = date.today()
    tomorrow: date = today + timedelta(1)

    return __loadHouseDetails(request, house, False, False, "", booking_error, comments, ratings, today, tomorrow, tiempo, temperatura, user_id)

@router.get("/{id}/edit", response_class = HTMLResponse)
def edit_house(request: Request, id: str, error: str = ""):
    user_id = __chechUser()
    if user_id == "None":
        return RedirectResponse("/login")

    house: dict = houses_api.get_by_id(id)

    return __loadHouseDetails(request, house, False, True, error, "", None, None, None, None, None, None, user_id)

@router.get("/{id}/delete")
def delete_house(request: Request, id: str):
    user_id = __chechUser()
    if user_id == "None":
        return RedirectResponse("/login")

    houses_api.delete(id)

    return my_houses(request)

@router.post("/{id}/addComment", response_class=HTMLResponse)
def add_comment(request: Request, id: str, comment: str = Form(title="coment")):
    user_id = __chechUser()
    if user_id == "None":
        return RedirectResponse("/login")

    message: MessagePost = MessagePost(sender_id=user_id, message=comment, house_id=id)
    messages_api.post(message)

    return house_details(request, id)
    
@router.post("/{id}/addRate", response_class=HTMLResponse)
def add_rate(request: Request, id: str, estrellas: int = Form()):
    user_id = __chechUser()
    if user_id == "None":
        return RedirectResponse("/login")

    ratings_api.create(user_id, None, id, estrellas)

    return house_details(request, id)


def __loadHouseDetails(request: Request, house: HousePost | dict, creating: bool, editing: bool, error: str, booking_error: str, comments: list | None, 
                       ratings: list | None, today_date: date | None, tomorrow_date: date | None, tiempo: dict | None, temperatura: dict | None, 
                       user_id: str):
    return templates.TemplateResponse("houseDetails.html", {"request": request, "house": house, "creating": creating, "editing": editing, 
                                                            "error": error, "booking_error": booking_error, "comments": comments, "ratings": ratings, 
                                                            "today_date": today_date, "tomorrow_date": tomorrow_date, "tiempo": tiempo, 
                                                            "temperatura": temperatura, "user_id": user_id})
    
# Private methods
def __chechUser():
    session = login_api.Singleton()
    if session.user is None:
        raise HTTPException(
            status_code=401, detail="No se ha iniciado sesión.")
    return session.user