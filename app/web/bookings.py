from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from datetime import date
from ..entities import bookings as bookings_api
from ..entities import houses as houses_api
from ..web import login as login_api
from ..entities.models import *
from . import houses

router = APIRouter()

templates = Jinja2Templates(directory="templates")

@router.get("/booked", response_class=HTMLResponse)
def my_bookings(request: Request):
    # List of bookings that you have booked
    user = __chechUser()
    return templates.TemplateResponse("bookings.html", {"request": request,
        "bookings": bookings_api.search(guest_id=user),
        "title": "Mis reservas"})

@router.get("/myHouses", response_class=HTMLResponse)
def houses_booked(request: Request):
    # List of bookings with your houses
    user = __chechUser()
    return templates.TemplateResponse("bookings.html", {"request": request,
        "bookings": bookings_api.get_by_house_owner_id(owner_id=user),
        "title": "Reservas de mis casas"})

@router.get("/{id}", response_class=HTMLResponse)
def booking_details(request: Request, id: str):
    # Booking details given its id
    user = __chechUser()
    booking = bookings_api.get_by_id(id)
    return templates.TemplateResponse("bookingDetails.html", {"request": request, "booking": booking, "house": houses_api.get_by_id(booking["house_id"]), "user": user, "State": State})

@router.post("/{id}/requestBooking", response_class=HTMLResponse)
def create_booking(request: Request, id: str, from_: date = Form(), to: date = Form(), guest_id: str = Form(), cost: str = Form()):
    # Create a new booking given a house id
    cost_float = float(cost)

    try:
        booking: BookingPost = BookingPost(house_id=id, from_=from_, to=to, guest_id=guest_id, cost=cost_float)
        inserted_booking = bookings_api.create(booking)
    except HTTPException as e:
        return houses.house_details(request, id, booking_error=e.detail)

    return booking_details(request, inserted_booking["id"])

@router.post("/{id}")
def update_booking_state(request: Request, id: str, state: State = Form()):
    # Update a booking from a form
    booking_cons: BookingConstructor = BookingConstructor(state=state)
    bookings_api.update(id=id, booking=booking_cons)
    return booking_details(request=request, id=id)

'''
@router.get("/{id}/chat")
def goto_chat(request: Request, id: str):
    # TODO
    # This will send you to the chat page of the booking
    return None
'''

# Private methods
def __chechUser():
    session = login_api.Singleton()
    if session.user is None:
        raise HTTPException(
            status_code=401, detail="No se ha iniciado sesión.")
    return session.user