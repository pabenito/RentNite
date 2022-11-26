# Import libraries
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Import modules
from .opendata import osm, aemet
from .entities import bookings, houses, users, ratings, messages, chats
from .web import bookings as bookings_web

# Create app
app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# Include modules
app.include_router(
    osm.router,
    prefix="/osm",
    tags=["opendata", "osm"]
)

app.include_router(
    aemet.router,
    prefix="/aemet",
    tags=["opendata", "aemet"]
)

app.include_router(
    bookings.router,
    prefix="/bookings",
    tags=["entities", "bookings"]
)

app.include_router(
    houses.router,
    prefix="/houses",
    tags=["entities", "houses"]
)

app.include_router(
    users.router,
    prefix="/users",
    tags=["entities", "users"]
)

app.include_router(
    ratings.router,
    prefix="/ratings",
    tags=["entities", "ratings"]
)

app.include_router(
    messages.router,
    prefix="/messages",
    tags=["entities", "messages"]
)

app.include_router(
    chats.router,
    prefix="/chats",
    tags=["entities", "chats"]
)

# Web

app.include_router(
    bookings_web.router,
    prefix="/web/bookings",
    tags=["web", "bookings"]
)



@app.get("/")
async def root():
    return {"message": "Welcome to Rentnite"}

@app.get("/login", response_class=HTMLResponse)
async def login(request:Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/profile", response_class=HTMLResponse)
async def login(request:Request):
    return templates.TemplateResponse("profile.html", {"request": request})

@app.get("/houses/", response_class=HTMLResponse)
async def red_houses(request: Request):
    return templates.TemplateResponse("offeredHouses.html", {"request": request}  )
