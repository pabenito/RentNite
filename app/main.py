# Import libraries
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Import modules
from .entities import router as entities
from .opendata import router as opendata
from .web import router as web

# Create app
app = FastAPI()

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
    tags=["entities"]
)

app.include_router(
    web.router,
    prefix="/web",
    tags=["web"]
)

@app.get("/")
async def root():
    return {"message": "Welcome to Rentnite"}
