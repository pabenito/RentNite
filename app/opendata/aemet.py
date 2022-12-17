# Import libraries
from typing import Union
from fastapi import Depends, APIRouter
from aemet_opendata.interface import AEMET
from datetime import datetime
import locale
from os import environ

# Create router
router = APIRouter()

# Initialize AEMET API
_api_key = environ["aemet_key"]
aemet = AEMET(api_key=_api_key)
aemet.api_debugging(True)

# Dependencies


# API
@router.get("/")
def root():
    return {"message": "Welcome to AEMET microservice"}

@router.get("/town")
def get_town(town: dict = Depends(aemet.get_town_by_coordinates)):
    return town

@router.get("/forecast/temperature/dailyPar")
def get_forecast_temperature_daily_urlParameters(town: dict = Depends(aemet.get_town_by_coordinates)):
    return get_temp_daily_from_map(aemet.get_specific_forecast_town_daily(town.get("id")))

@router.get("/forecast/temperature/daily")
def get_forecast_temperature_daily(latitude: Union[float, None] = None,longitude: Union[float, None] = None):
    town: dict = aemet.get_town_by_coordinates(latitude=latitude,longitude=longitude)
    return get_temp_daily_from_map(aemet.get_specific_forecast_town_daily(town.get("id")))    

@router.get("/forecast/temperature/hourly")
def get_forecast_temperature_hourly(town: dict = Depends(aemet.get_town_by_coordinates)):
    return get_temp_hourly_from_map(aemet.get_specific_forecast_town_daily(town.get("id")))

@router.get("/forecast/precipitation/dailyPar")
def get_forecast_precipitation_daily(latitude: Union[float, None] = None, longitude: Union[float, None] = None):
    town: dict = aemet.get_town_by_coordinates(latitude=latitude,longitude=longitude)
    return get_Daily_precipitation_from_map(aemet.get_specific_forecast_town_daily(town.get("id")))

@router.get("/forecast/precipitation/daily")
def get_forecast_precipitation_daily_urlParameters(town: dict = Depends(aemet.get_town_by_coordinates)):
    return get_Daily_precipitation_from_map(aemet.get_specific_forecast_town_daily(town.get("id")))  

@router.get("/forecast/precipitation/hourly")
def get_forecast_precipitation_hourly(town: dict = Depends(aemet.get_town_by_coordinates) ):
    return get_hourly_precipitation_from_map(aemet.get_specific_forecast_town_daily(town.get("id")))

    
# Auxiliary functions

DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"
locale.setlocale(locale.LC_TIME, "es_ES")

def get_temp_daily_from_map(map: dict):
    days : dict 
    days = map["data"][0]["prediccion"]["dia"]
    Aux : dict = {}
    for x in range(0,7):
        Aux[x]=days[x]["temperatura"]
        Aux[x]["dia"] = datetime.strptime(days[x]["fecha"], DATE_FORMAT).strftime("%a").capitalize()
        del Aux[x]["dato"]
    return Aux

def get_temp_hourly_from_map(map: dict):
    days : dict 
    days = map["data"][0]["prediccion"]["dia"]
    Aux : dict = {}
    for x in range(0,7):
        Aux[x]=days[x]["temperatura"]["dato"]
    return Aux

def get_Daily_precipitation_from_map(complete: dict):
    complete.pop("response")
    dias = complete["data"][0]["prediccion"]
    Dict = {}
    
    for x in range (0,7):
        Dict[x]=dias["dia"][x]["probPrecipitacion"][0]
    
    return Dict

def get_hourly_precipitation_from_map(complete: dict):
    complete.pop("response")
    dias = complete["data"][0]["prediccion"]
    Dict = {}
    
    for x in range (0,7):
        Dict[x]=dias["dia"][x]["probPrecipitacion"]
        del Dict[x][0]
    return Dict