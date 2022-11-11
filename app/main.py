# Import libraries
from fastapi import FastAPI

# Import modules
from .opendata import osm, aemet
from .entities import bookings, houses, users, ratings, messages, chats

# Create app
app = FastAPI()

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
    users.router,
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

@app.get("/")
async def root():
    return {"message": "Welcome to Rentnite"}







