from fastapi import APIRouter, Response, Cookie

router = APIRouter()

@router.post("/post_user/")
def create_cookie(response: Response,user: str):
    response.set_cookie(key="user", value=user)
    return response

@router.get("/user/")
def cookie_test(user: str | None = Cookie(default=None)):
    print("usuario" + user)
    return {"user": user}
