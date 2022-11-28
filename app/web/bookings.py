from fastapi import APIRouter, Request, Cookie, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from datetime import date
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

@router.post("/{id}/requestBooking", response_class=HTMLResponse)
def create_booking(request: Request, id: str, user = Cookie(default=None), state: State = Form(), from_: date = Form(), to: date = Form(), guest_id: str = Form(), cost: float = Form()):
    # Create a new booking given a house id
    booking: BookingPost = BookingPost(house_id=id, from_=from_, to=to, guest_id=guest_id, cost=cost)
    bookings_api.create(booking)