from branca.element import Figure
from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from folium import Map, Marker, Popup, Icon
from pydantic import BaseModel
import requests

from app.entities.models import House
from app.entities import houses as houses_api

base_url = "http://127.0.0.1:8000"
router = APIRouter()

class POI(BaseModel):
    latitude: float
    longitude: float
    color: str = "blue"
    popup: str = None
    icon: str = "circle"

def create_map(latitude: float, longitude: float, zoom: int = 17):
    return Map(location=[latitude, longitude], zoom_start=zoom)

def create_figure(width: int = 600, height: int = 400):
    return Figure(width=width, height=height)

def create_marker(
    latitude: float,
    longitude: float,
    color: str = "blue",
    icon: str = "circle",
    popup: str = None,
    popup_show: bool = True
):
    return Marker(
      location = [latitude, longitude],
      icon= Icon(color=color, icon=icon, prefix='fa'),
      popup = Popup(popup, show = popup_show) if popup else None
    )

def create_marker_house(
    latitude: float,
    longitude: float,
    address: str,
    color: str = "red",
    icon: str = "home",
    popup_show: bool = True
):
    return create_marker(latitude, longitude, color, icon, address, popup_show)

def create_marker_bus(
    latitude: float,
    longitude: float,
    number: int,
    color: str = "blue",
    icon: str = "bus",
    popup_show: bool = True
):
    return create_marker(latitude, longitude, color, icon, f"{number}", popup_show)

def plot(map: Map, width: int = 600, height: int = 400):
    figure = Figure(width=width, height=height)
    figure.add_child(map)
    return figure.render()

@router.post("/", response_class=HTMLResponse)
def marker(markers: list[POI], map: Map = Depends(create_map)):
    for poi in markers:
        poi: POI = poi 
        create_marker(**poi.dict(exclude_unset=True)).add_to(map)
    return plot(map)

@router.get("/marker", response_class=HTMLResponse)
def marker(map: Map = Depends(create_map), marker: Marker = Depends(create_marker)):
    marker.add_to(map)
    return plot(map)

@router.get("/bus", response_class=HTMLResponse)
def bus(map: Map = Depends(create_map), marker: Marker = Depends(create_marker_bus)):
    marker.add_to(map)
    return plot(map)

@router.get("/house", response_class=HTMLResponse)
def house(map: Map = Depends(create_map), marker: Marker = Depends(create_marker_house)):
    marker.add_to(map)
    return plot(map)

@router.get("/poi", response_class=HTMLResponse)
def poi(house_id: str):
    house: House = House.parse_obj(houses_api.get_by_id(house_id))
    map: Map = create_map(house.latitude, house.longitude)
    create_marker_house(house.latitude, house.longitude, house.address).add_to(map)
    buses: dict = requests.get(base_url + "/opendata/osm/maps/poi", params={"latitude":f"{house.latitude}", "longitude":f"{house.longitude}", "search":"bus_stop"}).json()
    for bus in buses.values():
        bus: dict = bus
        create_marker_bus(bus.get("lat"), bus.get("lon"), number=bus.get("tag").get("ref"), popup_show=False).add_to(map)
    return plot(map)

