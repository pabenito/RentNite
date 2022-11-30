# Import libraries
from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware


# Import modules
from .entities import router as entities
from .opendata import router as opendata
from .web import router as web

base_url = "http://127.0.0.1:8000"

# Create app
app = FastAPI()

# cors
origins = [
    "http://i.imgur.com",
    "https://i.imgur.com",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:8000/houses/#loaded"
    "https://127.0.0.1:8000",
    "https://127.0.0.1:8000/houses/#loaded"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# Include modules
app.include_router(
    opendata.router,
    prefix="/opendata",
    tags=["opendata"]
)

app.include_router(
    entities.router,
    prefix="/entities",
    tags=["entities"],
    
)

app.include_router(
    web.router,
    tags=["web"],
    
)



@app.get("/")
async def root():
    return {"message": "Welcome to Rentnite"}
