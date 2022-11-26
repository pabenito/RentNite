from fastapi import APIRouter, Response, Cookie

router = APIRouter()

@router.get("/login/")
def create_cookie(response: Response):
    response.set_cookie(key="user", value="my_username")

@router.get("/user/")
def create_cookie(user = Cookie(default=None)):
    return {"user": user}
