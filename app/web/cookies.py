from fastapi import APIRouter, Response, Cookie

router = APIRouter()

@router.get("/login/")
def create_cookie(response: Response):
    response.set_cookie(key="user", value="my_username")

@router.get("/user/")
def cookie_test(user = Cookie(default=None)):
    return {"user": user}
