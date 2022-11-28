from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from folium import Map, Circle, Marker, Popup, Icon
from branca.element import Figure

router = APIRouter()

def create_map(latitude: float, longitude: float, zoom: int = 17):
    return Map(location=[latitude, longitude], zoom_start=zoom)

def create_marker(latitude: float, longitude: float, color: str = "blue", popup: str = None, icon: str = "circle"):
    return Marker(
      location = [latitude, longitude],
      icon= Icon(color=color, icon=icon, prefix='fa'),
      popup = Popup(popup, show = True) if popup else None
    )

def create_marker_house(latitude: float, longitude: float, address: str, color: str = "red"):
    return create_marker(latitude, longitude, color, popup=address, icon="home")

def create_marker_bus(latitude: float, longitude: float, number: str, color: str = "blue"):
    return create_marker(latitude, longitude, color, popup=number, icon="bus")

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