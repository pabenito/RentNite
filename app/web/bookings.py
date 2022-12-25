from typing import Union
from fastapi import APIRouter, Request, Form, HTTPException, Cookie, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import date
from ..entities import bookings as bookings_api
from ..entities import houses as houses_api
from ..entities import chats as chats_api
from ..entities.models import *
from ..payments import pay
from . import houses

router = APIRouter()

templates = Jinja2Templates(directory="templates")

@router.get("/booked", response_class=HTMLResponse)
def my_bookings(request: Request, user_id: Union[str, None] = Cookie(default=None)):
    # List of bookings that you have booked
    user = user_id
    if user is None:
        return RedirectResponse("/login")

    return templates.TemplateResponse("bookings.html", {"request": request,
        "bookings": bookings_api.search(guest_id=str(user)),
        "title": "Mis reservas",
        "user_id": str(user)})

@router.get("/myHouses", response_class=HTMLResponse)
def houses_booked(request: Request, user_id: Union[str, None] = Cookie(default=None)):
    # List of bookings with your houses
    user = user_id
    if user is None:
        return RedirectResponse("/login")

    return templates.TemplateResponse("bookings.html", {"request": request,
        "bookings": bookings_api.get_by_house_owner_id(owner_id=str(user)),
        "title": "Reservas de mis casas",
        "user_id": str(user)})

@router.get("/{id}", response_class=HTMLResponse)
def booking_details(request: Request, id: str, user_id: Union[str, None] = Cookie(default=None)):
    # Booking details given its id
    user = user_id
    if user is None:
        return RedirectResponse("/login")

    booking = bookings_api.get_by_id(id)
    return templates.TemplateResponse("bookingDetails.html", {"request": request, "booking": booking, "house": houses_api.get_by_id(booking["house_id"]), "user_id": str(user), "State": State})

@router.post("/{id}/requestBooking", response_class=HTMLResponse)
def create_booking(request: Request, id: str, from_: date = Form(), to: date = Form(), guest_id: str = Form(), cost: str = Form(), nonce: str = Form(), user_id: Union[str, None] = Cookie(default=None)):
    # Create a new booking given a house id
    user = user_id
    if user is None:
        return RedirectResponse("/login", status_code = status.HTTP_302_FOUND)

    cost_float = float(cost)

    try:
        booking: BookingPost = BookingPost(house_id=id, from_=from_, to=to, guest_id=guest_id, cost=cost_float)
        inserted_booking = bookings_api.create(booking)
    except HTTPException as e:
        return houses.house_details(request, id, booking_error=e.detail, user_id = user_id)

    pay(cost, nonce)

    return booking_details(request, inserted_booking["id"], user_id)

@router.post("/{id}")
def update_booking_state(request: Request, id: str, state: State = Form(), user_id: Union[str, None] = Cookie(default=None)):
    # Update a booking from a form
    user = user_id
    if user is None:
        return RedirectResponse("/login", status_code = status.HTTP_302_FOUND)

    booking_cons: BookingConstructor = BookingConstructor(state=state)
    bookings_api.update(id=id, booking=booking_cons)
    return booking_details(request=request, id=id, user_id=user_id)


@router.get("/{id}/chat")
def goto_chat(id: str, user_id: Union[str, None] = Cookie(default=None)):
    if user_id is None:
        return RedirectResponse("/login")

    chat_id = chats_api.get(id, None, None, None, None, None, None)[0]["id"]
    return RedirectResponse(f"/chats/{chat_id}", status_code = status.HTTP_303_SEE_OTHER)