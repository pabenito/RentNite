from osmapi import OsmApi
from fastapi import Depends, FastAPI

app = FastAPI()

@app.get("/osm/node/{id}")
async def get_node(id:int, osm=Depends(OsmApi)):
    return osm.NodeGet(id)

@app.get("/osm/map")
async def get_map(lon:float, lat:float, range:float=1, osm=Depends(OsmApi)):
    min_longitude, min_latitude, max_longitude, max_latitude = coordinates_to_map_range(lon, lat, range)
    return osm.Map(min_longitude, min_latitude, max_longitude, max_latitude)

def kilometers_to_degrees(kilometers:float):
    return kilometers/111 # One longitude or latitude degree diference is 111 km distance

def coordinates_to_map_range(longitude:float, latitude:float, kilometers:float):
    min_longitude = longitude - kilometers_to_degrees(kilometers)
    min_latitude = latitude - kilometers_to_degrees(kilometers)
    max_longitude = longitude + kilometers_to_degrees(kilometers)
    max_latitude = latitude + kilometers_to_degrees(kilometers)
    return min_longitude, min_latitude, max_longitude, max_latitude







