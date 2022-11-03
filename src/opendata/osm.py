# Immport libraries
from osmapi import OsmApi
from fastapi import Depends, APIRouter

# Create router
router = APIRouter()

# Dependencies
def get_map(latitude: float, longitude: float, range: float=1, osm: OsmApi = Depends(OsmApi)):
    return map_list_to_dict(osm.Map(*coordinates_to_map_range(latitude, longitude, range)))

def get_poi(search:str,map: dict = Depends(get_map)):
    if search == "bus":
        return get_bus_nodes_from_map(map, only_with_tags=True)
    else:
        return get_nodes_from_map(map, only_with_tags=True)

# API

@router.get("/nodes/{id}")
async def get_node(id:int, osm=Depends(OsmApi)):
    return osm.NodeGet(id)

@router.get("/maps/poi")
async def get_map_poi(bus : str= Depends(get_poi),map: dict = Depends(get_poi)):
    return map

@router.get("/maps/all")
async def get_map_all(map: dict = Depends(get_map)):
    return map

@router.get("/maps/poi/bus")
async def get_map_poi(map: dict = Depends(get_poi)):
    return map

# Auxiliary functions


def map_list_to_dict(map: list):
    map_dict : dict = {}
    for item in map:
        id = item.get("data").get("id")
        item.get("data").pop("id")
        item.get("data")["type"]=item.get("type")
        map_dict[id]=item.get("data")
    return map_dict

def get_nodes_from_map(map: dict, only_with_tags: bool = False):
    for id in list(map.keys()):
        if map.get(id).get("type")!="node":
            map.pop(id)
        elif only_with_tags and not map.get(id).get("tag") : # Any tag
            map.pop(id)
    return map

def get_bus_nodes_from_map(map: dict, only_with_tags: bool = False):
    for id in list(map.keys()):
        if map.get(id).get("type")!="node":
            map.pop(id)
        elif only_with_tags and len(map.get(id).get("tag")) < 2 : # Any tag
            map.pop(id)
    return map

def have_common_members(a: set, b: set):
    return len(a.intersection(b)) > 0

def kilometers_to_degrees(kilometers: float):
    return kilometers/111 # One longitude or latitude degree diference is 111 km distance

def coordinates_to_map_range(latitude: float, longitude: float, kilometers: float):
    min_longitude = longitude - kilometers_to_degrees(kilometers)
    min_latitude = latitude - kilometers_to_degrees(kilometers)
    max_longitude = longitude + kilometers_to_degrees(kilometers)
    max_latitude = latitude + kilometers_to_degrees(kilometers)
    return min_longitude, min_latitude, max_longitude, max_latitude







