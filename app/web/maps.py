from fastapi import APIRouter, Depends
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

def create_marker(poi: POI):
    return Marker(
      location = [poi.latitude, poi.longitude],
      icon= Icon(color=poi.color, icon=poi.icon, prefix='fa'),
      popup = Popup(poi.popup, show = True) if poi.popup else None
    )

def create_marker_house(house: House):
    return create_marker(house)

def create_marker_bus(bus: Bus):
    return create_marker(bus)

def plot(map: Map, marker: Marker, width: int = 600, height: int = 400):
    fig = Figure(width=width, height=height)
    marker.add_to(map)
    fig.add_child(map)
    return fig.render()

@router.post("/marker", response_class=HTMLResponse)
def marker(map: Map = Depends(create_map), marker: Marker = Depends(create_marker)):
    return plot(map, marker)

@router.post("/bus", response_class=HTMLResponse)
def bus(map: Map = Depends(create_map), marker: Marker = Depends(create_marker_bus)):
    return plot(map, marker)

@router.post("/house", response_class=HTMLResponse)
def house(map: Map = Depends(create_map), marker: Marker = Depends(create_marker_house)):
    return plot(map, marker)