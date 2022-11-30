from fastapi import APIRouter, Request, Cookie, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from ..entities import users as users_api
from ..entities import ratings as ratings_api
from app.entities import models
from app.web import login

router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
def perfil_usuario(request: Request):
    s = None
    if login.get_current_user():
        s = login.Singleton()

    return templates.TemplateResponse("profile.html", {"request": request, "user": users_api.get_by_id(s.user), "rating": ratings_api.get(None, s.user, None, None, None, None, None), "identificador": s.user})


@router.post("/{id}/addRate", response_class=HTMLResponse)
def add_Rate(request: Request, id: str, estrellas: int = Form()):
    s = login.Singleton()
    ratings_api.create(s.user, id, None, estrellas)

    return perfil_usuario(request)
