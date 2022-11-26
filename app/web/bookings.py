from fastapi import APIRouter, Request, Cookie
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from ..entities import bookings as bookings_api

router = APIRouter()

templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
def read_item(request: Request):
    return templates.TemplateResponse("bookingsGuest.html", {"request": request, "bookings": bookings_api.get(), "img": "https://www.eldiariodecarlospaz.com.ar/u/fotografias/fotosnoticias/2020/9/6/137680.jpg"})