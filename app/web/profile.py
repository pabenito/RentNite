from fastapi import APIRouter, Request, Cookie, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from ..entities import users as users_api
from ..entities import ratings as ratings_api
from app.entities import models

router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
def usuraios(request: Request, user=Cookie(default=None)):
    return templates.TemplateResponse("profile.html", {"request": request, "user": user})


@router.get("/{id}", response_class=HTMLResponse)
def perfil_usuario(request: Request, id: str):
    #id = "636ad4aa5baf6bcddce08814"
    return templates.TemplateResponse("profile.html", {"request": request, "user": users_api.get_by_id(id), "rating": ratings_api.get(None, id, None, None, None, None, None)})


@router.post("/{id}/addRate", response_class=HTMLResponse)
def add_Rate(request: Request, id: str, estrellas: int = Form()):
    ratings_api.create("636ad4aa5baf6bcddce08814", id, None, estrellas)

    return perfil_usuario(request, id)
