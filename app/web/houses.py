from fastapi import APIRouter, Request, Cookie, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from ..entities import houses as houses_api
from ..entities import messages as messages_api
from ..entities import ratings as ratings_api
from ..entities.models import MessagePost, HouseConstructor, HousePost
from datetime import date
from ..opendata import aemet as aemet_api
from ..entities.models import *

router = APIRouter()

templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
def read_item(request: Request):
    return templates.TemplateResponse("offeredHouses.html", {"request": request, "houses": houses_api.get()})

@router.get("/myHouses", response_class=HTMLResponse)
def my_houses(request: Request, user = Cookie(default=None)):
    return templates.TemplateResponse("myHouses.html", {"request": request, "houses": houses_api.get(owner_id="636ad4aa5baf6bcddce08814")})

@router.get("/create")
def create_house(request: Request, user = Cookie(default=None)):
    house: HouseConstructor = HouseConstructor(address = "", capacity = 1, price = 0, rooms = 1, bathrooms = 1, owner_name = None,
                                               owner_id = "636ad4aa5baf6bcddce08814",
                                               image = "https://live.staticflickr.com/65535/52527243603_413f2bc2c3_n.jpg",
                                               longitude = 0, latitude = 0)

    return templates.TemplateResponse("houseDetails.html", {"request": request, "house": house, "creating": True, 
                                                            "editing": False, "error": "", "user": user})

@router.post("/save", response_class=HTMLResponse)
def update_house(request: Request, user = Cookie(default=None), id: str = Form(), address: str = Form(), capacity: int = Form(), price: str = Form(),
               rooms: int = Form(), bathrooms: int = Form(), latitude: str = Form(), longitude: str = Form()):
    try:
        price_float: float = float(price)
        latitude_float: float = float(latitude)
        longitude_float: float = float(longitude)

        if id == "None":
            house = HousePost(address = address, capacity = capacity, price = price_float, rooms = rooms, bathrooms = bathrooms, 
                                     owner_id = "636ad4aa5baf6bcddce08814", image = "https://live.staticflickr.com/65535/52527243603_413f2bc2c3_n.jpg", 
                                     longitude = longitude_float, latitude = latitude_float)
            house = houses_api.create(house)
            id = house["id"]
        else:
            house = HouseConstructor(address=address, capacity = capacity, price = price_float, rooms = rooms, bathrooms = bathrooms, 
                                                       owner_name = "Victor Lopez", owner_id = "636ad4aa5baf6bcddce08814", 
                                                       image = "https://live.staticflickr.com/65535/52527243603_413f2bc2c3_n.jpg", 
                                                       longitude = longitude_float, latitude=latitude_float)
            houses_api.update(id, house)

        return my_houses(request, user)
    except:
        return edit_house(request, id, user, "Los valores introducidos no son validos.")

@router.get("/{id}", response_class=HTMLResponse)
def house_details(request: Request, id: str, user = Cookie(default=None), booking_error: str = ""):
    house : House = houses_api.get_by_id(id)
    return templates.TemplateResponse("houseDetails.html", {"request": request, "house": house, "creating": False, 
                                                            "editing": False, "comments": messages_api.get(None, id, None, None, None),
                                                            "ratings": ratings_api.get(None,None,None,id,None,None,None), 
                                                            "date": date.today(), "booking_error": booking_error, "user": user,
                                                            "tiempo": aemet_api.get_forecast_precipitation_daily(latitude=house["latitude"],longitude=house["longitude"]),
                                                            "temperatura": aemet_api.get_forecast_temperature_daily(latitude=house["latitude"],longitude=house["longitude"]) })

@router.get("/{id}/edit", response_class=HTMLResponse)
def edit_house(request: Request, id: str, user = Cookie(default=None), error: str = ""):
    return templates.TemplateResponse("houseDetails.html", {"request": request, "house": houses_api.get_by_id(id), "creating": False,
                                                            "editing": True, "error": error, "user": user})

@router.get("/{id}/delete")
def delete_house(request: Request, id: str, user = Cookie(default=None)):
        houses_api.delete(id)
        return my_houses(request, user)

@router.post("/{id}/addComment", response_class=HTMLResponse)
def add_comment(request: Request, id: str, user = Cookie(default=None), comment: str = Form(title="coment")):
    message: MessagePost = MessagePost(sender_id="636ad4aa5baf6bcddce08814", message=comment, house_id=id)
    messages_api.post(message)
    return house_details(request, id, user)
    
@router.post("/{id}/addRate", response_class=HTMLResponse)
def add_rate(request: Request, id: str, user = Cookie(default=None), estrellas:int = Form() ):
    ratings_api.create("636ad4aa5baf6bcddce08814",None,id,estrellas)
    return house_details(request, id, user)

