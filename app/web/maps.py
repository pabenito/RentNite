from fastapi import APIRouter, Depends, Body
from pydantic import BaseModel, Field
from fastapi.responses import HTMLResponse
from folium import Map, Circle, Marker, Popup, Icon
from branca.element import Figure

router = APIRouter()

class POI(BaseModel):
    latitude: float
    longitude: float
    color: str = "blue"
    popup: str = None
    icon: str = "circle"

class House(POI):
    color: str = "red"
    popup: str = Field(alias="address"), 
    icon: str = "home"

class Bus(POI):
    color: str = "blue"
    popup: str = Field(alias="number"), 
    icon: str = "bus"

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
):
    return Marker(
      location = [latitude, longitude],
      icon= Icon(color=color, icon=icon, prefix='fa'),
      popup = Popup(popup, show = True) if popup else None
    )

def create_marker_house(
    latitude: float,
    longitude: float,
    address: str,
    color: str = "red",
    icon: str = "home",
):
    return create_marker(latitude, longitude, color, icon, address)

def create_marker_bus(
    latitude: float,
    longitude: float,
    number: str,
    color: str = "blue",
    icon: str = "bus",
):
    return create_marker(latitude, longitude, color, icon, number)

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
    return plot(map, marker)

@router.get("/house", response_class=HTMLResponse)
def house(map: Map = Depends(create_map), marker: Marker = Depends(create_marker_house)):
    marker.add_to(map)
    return plot(map, marker)