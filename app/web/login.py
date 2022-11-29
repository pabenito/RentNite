from fastapi import APIRouter, Request, Cookie, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from ..entities import users as users_api
from .profile import perfil_usuario


router = APIRouter()

templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
def login(request: Request,user = Cookie(default=None)):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/do", response_class=HTMLResponse)
def do_login(request: Request, email:str = Form()):
    return templates.TemplateResponse("profile.html", {"request": request})
