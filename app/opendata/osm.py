# Import libraries
from osmapi import OsmApi
from fastapi import Depends, APIRouter
from geopy.geocoders import Nominatim

# Create router
router = APIRouter()

# Dependencies
def get_map(latitude: float, longitude: float, range: float=1, osm: OsmApi = Depends(OsmApi)):
    return __map_list_to_dict(osm.Map(*__coordinates_to_map_range(latitude, longitude, range)))

def get_poi(search: str | None = None, map: dict = Depends(get_map)):
    return __get_nodes_from_map(map, search, only_with_tags=True)

# API
@router.get("/")
async def root():
    return {"message": "Welcome to OpenStreetMap microservice"}

@router.get("/nodes/{id}")
async def get_node(id:int, osm=Depends(OsmApi)):
    return osm.NodeGet(id)

@router.get("/maps/poi")
async def get_map_poi(map: dict = Depends(get_poi)):
    return map

@router.get("/maps/all")
async def get_map_all(map: dict = Depends(get_map)):
    return map

# Geocoding

geolocator = Nominatim(user_agent="RentNite")

def geocode(address: str):
    return geolocator.geocode(address) 

# Auxiliary functions

def __map_list_to_dict(map: list):
    map_dict : dict = {}
    for item in map:
        id = item.get("data").get("id")
        item.get("data").pop("id")
        item.get("data")["type"]=item.get("type")
        map_dict[id]=item.get("data")
    return map_dict

def __get_nodes_from_map(map: dict, search: str | None = None, only_with_tags: bool = False):
    for id in list(map.keys()):
        if map.get(id).get("type")!="node":
            map.pop(id)
        elif not search and only_with_tags and  len(map.get(id).get("tag")) < 2 : # Any tag
            map.pop(id)
        elif search and only_with_tags and not search in map.get(id).get("tag").values(): # Bus_Stop/Restaurant/Subway Tag
            map.pop(id)
        
    return map


def __have_common_members(a: set, b: set):
    return len(a.intersection(b)) > 0

def __kilometers_to_degrees(kilometers: float):
    return kilometers/111 # One longitude or latitude degree diference is 111 km distance

def __coordinates_to_map_range(latitude: float, longitude: float, kilometers: float):
    min_longitude = longitude - __kilometers_to_degrees(kilometers)
    min_latitude = latitude - __kilometers_to_degrees(kilometers)
    max_longitude = longitude + __kilometers_to_degrees(kilometers)
    max_latitude = latitude + __kilometers_to_degrees(kilometers)
    return min_longitude, min_latitude, max_longitude, max_latitude







