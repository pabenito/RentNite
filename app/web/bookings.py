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
    # List of all bookings
    return templates.TemplateResponse("bookings.html", {"request": request, "bookings": bookings_api.get()})

@router.get("/booked", response_class=HTMLResponse)
def my_bookings(request: Request, user = Cookie(default=None)):
    # List of bookings that you have booked
    user = "Asier Gallego"
    return templates.TemplateResponse("bookings.html", {"request": request, "bookings": bookings_api.search(guest_name=user), "kind": "as_guest"})

@router.get("/myHouses", response_class=HTMLResponse)
def houses_booked(request: Request, user = Cookie(default=None)):
    # List of bookings with your houses
    user = "Asier Gallego"
    return templates.TemplateResponse("bookings.html", {"request": request, "bookings": bookings_api.get_by_house_owner_name(owner_name=user), "kind": "as_owner"})

@router.get("/{id}", response_class=HTMLResponse)
def booking_details(request: Request, id: str):
    # Booking details given its id
    user = "Asier Gallego"
    booking = bookings_api.get_by_id(id)
    return templates.TemplateResponse("bookingDetails.html", {"request": request, "booking": booking, "house": houses_api.get_by_id(booking["house_id"]), "user": user, "State": State})

@router.post("/{id}/requestBooking", response_class=HTMLResponse)
def create_booking(request: Request, id: str, from_: date = Form(), to: date = Form(), guest_id: str = Form(), cost: str = Form()):
    # Create a new booking given a house id
    cost = cost[-2]
    cost_float: float = float(cost)
    booking: BookingPost = BookingPost(house_id=id, from_=from_, to=to, guest_id=guest_id, cost=cost_float)
    bookings_api.create(booking)

@router.put("/{id}")
def update_booking(request: Request, id: str, from_: date | None = Form(), to: date | None = Form(), cost: float | None = Form(), state: State | None = Form()):
    # Update a booking from a form
    bookings_api.update(id=id, state=state, from_=from_, to=to, cost=cost)