from fastapi import APIRouter
from . import bookings, houses, profile, login, maps

router = APIRouter()

router.include_router(
    bookings.router,
    prefix="/bookings",
    tags=["bookings"]
)

router.include_router(
    houses.router,
    prefix="/houses",
    tags=["houses"]
)

router.include_router(
    profile.router,
    prefix="/profile",
    tags=["profile"]
)

router.include_router(
    login.router,
    prefix="/login",
    tags=["login"]
)

router.include_router(
    maps.router,
    prefix="/map",
    tags=["map"]
)