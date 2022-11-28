from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from fastapi.responses import HTMLResponse
from folium import Map, Circle, Marker, Popup, Icon
from branca.element import Figure

router = APIRouter()

def create_map(latitude: float, longitude: float, zoom: int = 17):
    return Map(location=[latitude, longitude], zoom_start=zoom)

def create_marker(
    latitude: float,
    longitude: float,
    color: str = "blue",
    icon: str = "circle",
    popup: str = None,
):
    return Marker(
      location = [poi.latitude, poi.longitude],
      icon= Icon(color=poi.color, icon=poi.icon, prefix='fa'),
      popup = Popup(poi.popup, show = True) if poi.popup else None
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

def plot(map: Map, marker: Marker, width: int = 600, height: int = 400):
    fig = Figure(width=width, height=height)
    marker.add_to(map)
    fig.add_child(map)
    return fig.render()

@router.get("/marker", response_class=HTMLResponse)
def marker(map: Map = Depends(create_map), marker: Marker = Depends(create_marker)):
    return plot(map, marker)

@router.get("/bus", response_class=HTMLResponse)
def bus(map: Map = Depends(create_map), marker: Marker = Depends(create_marker_bus)):
    return plot(map, marker)

@router.get("/house", response_class=HTMLResponse)
def house(map: Map = Depends(create_map), marker: Marker = Depends(create_marker_house)):
    return plot(map, marker)