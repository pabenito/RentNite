# Immport libraries
from osmapi import OsmApi
from fastapi import Depends, APIRouter

# Create router
router = APIRouter()

# Dependencies
def get_map(lon: float, lat: float, range: float=1, osm: OsmApi = Depends(OsmApi)):
    return map_list_to_dict(osm.Map(*coordinates_to_map_range(lon, lat, range)))

def get_poi(map: dict = Depends(get_map)):
    return get_nodes_from_map(map)

# API

@router.get("/node/{id}")
async def get_node(id:int, osm=Depends(OsmApi)):
    return osm.NodeGet(id)

@router.get("/map/poi")
async def get_map_poi(map: dict = Depends(get_poi)):
    print(type(map))
    return map

@router.get("/map/all")
async def get_map_all(map: dict = Depends(get_map)):
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

def get_nodes_from_map(map: dict, tags: set | None = None):
    print("Map kays",list(map.keys()))
    for id in list(map.keys()):
        if map.get(id).get("type")!="node":
            print(f"Eliminamos {id} proque no es un nodo")
            map.pop(id)
        elif tags == {"*"} and not map.get(id).get("tag"): # Any tag
            print(f"Eliminamos {id} proque no tiene tag: {map.get(id)}")
            map.pop(id)
        elif tags and not have_common_members(tags, set(map.get(id).get("tag").keys())): # specific tags
            map.pop(id)
    return map

def have_common_members(a: set, b: set):
    return len(a.intersection(b)) > 0

def kilometers_to_degrees(kilometers: float):
    return kilometers/111 # One longitude or latitude degree diference is 111 km distance

def coordinates_to_map_range(longitude: float, latitude: float, kilometers: float):
    min_longitude = longitude - kilometers_to_degrees(kilometers)
    min_latitude = latitude - kilometers_to_degrees(kilometers)
    max_longitude = longitude + kilometers_to_degrees(kilometers)
    max_latitude = latitude + kilometers_to_degrees(kilometers)
    return min_longitude, min_latitude, max_longitude, max_latitude







