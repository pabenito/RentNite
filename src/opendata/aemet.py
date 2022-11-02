# Import libraries
from fastapi import Depends, APIRouter
from aemet_opendata.interface import AEMET

# Create router
router = APIRouter()

# Initialize AEMET API
_api_key = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJyYXVsZG9mZUB1bWEuZXMiLCJqdGkiOiJjYmFiODMwMi1kMzg2LTQ1OGQtOGY1NS04NmFhMTcwOTBmYjgiLCJpc3MiOiJBRU1FVCIsImlhdCI6MTY2NjcyMTA0OCwidXNlcklkIjoiY2JhYjgzMDItZDM4Ni00NThkLThmNTUtODZhYTE3MDkwZmI4Iiwicm9sZSI6IiJ9.rp2l5Z70ecrGMr0PiqVhfiXckkkaHlBkeCmuB487Y3c"
aemet = AEMET(api_key=_api_key)
aemet.api_debugging(True)

# Dependencies


# API
@router.get("/")
async def root():
    return {"message": "Welcome to AEMET open data API"}

@router.get("/stations")
async def get_station(station: dict = Depends(aemet.get_climatological_values_station_by_coordinates)):
    return station

@router.get("/town")
async def get_town(town: dict = Depends(aemet.get_town_by_coordinates)):
    return town

@router.get("/forecast/daily")
async def get_forecast_daily(town: dict = Depends(aemet.get_town_by_coordinates)):
    return get_temp_from_map(aemet.get_specific_forecast_town_daily(town.get("id")))

@router.get("/forecast/hourly")
async def get_forecast_hourly(town: dict = Depends(aemet.get_town_by_coordinates)):
    return aemet.get_specific_forecast_town_hourly(town.get("id"))

    
# Auxiliary functions


def get_temp_from_map(map: dict):
    days : dict 
    days = map["data"][0]["prediccion"]["dia"]
    Aux : dict = {}
    for x in range(0,6):
        Aux[x]=days[x]["temperatura"]
    return Aux

def get_Daily_precipitation_from_map(complete: dict):
    complete.pop("response")
    dias = complete["data"][0]["prediccion"]
    Dict = {}
    
    for x in range (0,7):
        Dict[x]=dias["dia"][x]["probPrecipitacion"][0]
    
    return Dict