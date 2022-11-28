from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from folium import Map
from branca.element import Figure

router = APIRouter()

@router.get("/plot", response_class=HTMLResponse)
def plot(longitude: float, latitude: float, zoom: int = 15):
    fig = Figure(width=600, height=400)
    mapa = Map(location=[longitude, latitude], zoom_start=zoom)
    fig.add_child(mapa)
    return fig.render()