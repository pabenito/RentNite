from fastapi import APIRouter
from . import aemet, osm

router = APIRouter()

router.include_router(
    aemet.router,
    prefix="/aemet",
    tags=["aemet"]
)

router.include_router(
    osm.router,
    prefix="/osm",
    tags=["osm"]
)