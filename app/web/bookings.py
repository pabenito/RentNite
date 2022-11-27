from fastapi import APIRouter, Request, Cookie
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from ..entities import bookings as bookings_api

router = APIRouter()

templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
def list_bookings(request: Request):
    return templates.TemplateResponse("bookingsGuest.html", {"request": request, "bookings": bookings_api.search(guestName="Asier Gallego")})

@router.get("/{id}", response_class=HTMLResponse)
def booking_details(request: Request, id: str):
    return templates.TemplateResponse("bookingDetails.html", {"request": request, "booking": bookings_api.get_by_id(id)})
