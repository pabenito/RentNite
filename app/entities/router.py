from fastapi import APIRouter
from . import bookings, houses, users, ratings, messages, chats

router = APIRouter()

router.include_router(
    bookings.router,
    prefix="/bookings",
    tags=["bookings"]
)

router.include_router(
    houses.router,
    prefix="/houses",
    tags=["houses"],
)

router.include_router(
    users.router,
    prefix="/users",
    tags=["users"]
)

router.include_router(
    ratings.router,
    prefix="/ratings",
    tags=["ratings"]
)

router.include_router(
    messages.router,
    prefix="/messages",
    tags=["messages"]
)

router.include_router(
    chats.router,
    prefix="/chats",
    tags=["chats"]
)