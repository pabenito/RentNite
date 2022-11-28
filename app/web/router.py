from fastapi import APIRouter
from . import bookings, cookies, maps

router = APIRouter()

router.include_router(
    bookings.router,
    prefix="/bookings",
    tags=["bookings"]
)

router.include_router(
    cookies.router,
    prefix="/cookies",
    tags=["cookies"]
)

router.include_router(
    maps.router,
    prefix="/map",
    tags=["map"]
)