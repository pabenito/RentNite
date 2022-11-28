from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from folium import Map, Circle
from branca.element import Figure

router = APIRouter()

@router.get("/plot", response_class=HTMLResponse)
def plot(latitude: float, longitude: float, zoom: int = 17, radius: int = 15, color: str = "blue", fill: bool = True):
    fig = Figure(width=600, height=400)
    map = Map(location=[latitude, longitude], zoom_start=zoom)
    marker = Circle(
      location = [latitude, longitude],
      radius = radius,
      color = color,
      fill = fill
    )
    marker.add_to(map)
    fig.add_child(map)
    return fig.render()