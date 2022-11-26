from fastapi import APIRouter, Request, Cookie
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from ..entities import users as users_api

router = APIRouter()

templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
def read_item(request: Request,user = Cookie(default=None)):
    return templates.TemplateResponse("profile.html", {"request": request, "user": user})