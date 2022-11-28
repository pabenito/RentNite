from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from folium import Map, Circle, Marker, Popup
from branca.element import Figure

router = APIRouter()

def create_map(latitude: float, longitude: float, zoom: int = 17):
    return Map(location=[latitude, longitude], zoom_start=zoom)

def create_marker(latitude: float, longitude: float, radius: int = 15, color: str = "blue", fill: bool = True, popup: str = None):
    return Marker(
      location = [latitude, longitude],
      radius = radius,
      color = color,
      fill = fill,
      popup = Popup(popup, show = True if popup else False)
    )

@router.get("/plot", response_class=HTMLResponse)
def plot(map: Map = Depends(create_map), marker: Marker = Depends(create_marker)):
    fig = Figure(width=600, height=400)
    marker.add_to(map)
    fig.add_child(map)
    return fig.render()