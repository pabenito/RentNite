from fastapi import APIRouter, Request, Cookie, Form, HTTPException, Response
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from ..entities import users as users_api
from ..entities import ratings as ratings_api
from app.entities import models
from app.web import cookies
from app.web import login


router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
def perfil_usuario(request: Request):
    user = __chechUser()
    return templates.TemplateResponse("profile.html", {"request": request, "user": users_api.get_by_id(user), "rating": ratings_api.get(None,user, None, None, None, None, None), "identificador": user})


@router.post("/{id}/addRate", response_class=HTMLResponse)
def add_Rate(request: Request, id: str, estrellas: int = Form(),user: str | None = Cookie(default=None)):
    user = __chechUser()
    ratings_api.create(user, id, None, estrellas)
    return perfil_usuario(request)


# Private methods
def __chechUser():
    session = login.Singleton()
    if session is None:
        raise HTTPException(
            status_code=401, detail="No se ha iniciado sesión.")
    return session.user
