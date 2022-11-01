# Immport libraries
from fastapi import FastAPI

# Import modules
from opendata import osm

# Create app
app = FastAPI()

# Include modules
app.include_router(
    osm.router,
    prefix="/osm",
    tags=["opendata", "osm"]
)

@app.get("/")
async def root():
    return {"message": "Welcome to Rentnite"}








