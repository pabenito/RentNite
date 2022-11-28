from fastapi import APIRouter, Request, Cookie
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from ..entities import bookings as bookings_api
from ..entities import houses as houses_api
from ..entities.models import *

router = APIRouter()

templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
def list_bookings(request: Request):
    return templates.TemplateResponse("bookings.html", {"request": request, "bookings": bookings_api.get()})

@router.get("/booked", response_class=HTMLResponse)
def my_bookings(request: Request, user = Cookie(default=None)):
    return templates.TemplateResponse("bookings.html", {"request": request, "bookings": bookings_api.search(guest_name=user)})

@router.get("/{id}", response_class=HTMLResponse)
def booking_details(request: Request, id: str):
    user = "Asier Gallego"
    booking = bookings_api.get_by_id(id)
    return templates.TemplateResponse("bookingDetails.html", {"request": request, "booking": booking, "house": houses_api.get_by_id(booking["house_id"]), "user": user, "State": State})