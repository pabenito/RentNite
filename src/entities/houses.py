from fastapi import Depends, APIRouter

router = APIRouter()

@router.get("/")
async def root():
    return {"message": "Welcome to AEMET open data API"}