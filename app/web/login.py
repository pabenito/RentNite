from typing import Union
from fastapi import APIRouter, Request, Cookie, Depends, Form, HTTPException, status, Response, Body
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from ..entities import users as users_api
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.hash import sha256_crypt
from ..entities.models import *
from fastapi_sso.sso.google import GoogleSSO
from os import environ
import requests

google_sso = GoogleSSO(
    environ["GOOGLE_CLIENT_ID"],
    environ["GOOGLE_CLIENT_SECRET"],
    environ["APP_URL"]
)

base_url=environ["base_url"]

router = APIRouter()

templates = Jinja2Templates(directory="templates")

# OAUTH2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')

@router.get("/", response_class=HTMLResponse)
def login(request: Request, login_error: str = "", registration_error: str = "", registration_success_message: str = ""):
    return templates.TemplateResponse("login.html", {"request": request, "login_error": login_error, "registration_error": registration_error,
                                                     "registration_success_message": registration_success_message})

# Usuario con contraseña

async def authenticate_user(email: str, password: str):
    user = users_api.general_get(email=email)
    if user is None:
        return False

    if not verify_password(user, password):
        return False
    return user["id"]


def verify_password(user: User, password: str):
    return sha256_crypt.verify(password, user["password_hash"])


@router.post("/register", response_class=HTMLResponse)
def create_user(request: Request, username: str = Form(), correo: str = Form(), password: str = Form()):
    try:
       users_api.create(username, correo, password)
        # user: UserPost = UserPost(username=username,email=email,password_hash=password)
    except HTTPException as e:
        return login(request, registration_error=e.detail)

    return login(request, registration_success_message="Usuario registrado con exito")

@router.post('/token')
async def generate_token(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    user_id = await authenticate_user(form_data.username, form_data.password)
    if not user_id:
        return login(request, "Usuario o contraseña no validos")
    response = RedirectResponse(base_url, status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie("user_id", user_id)
    return response

# Google

@router.get("/google")
async def google_login():
    """Generate login url and redirect"""
    return await google_sso.get_login_redirect()

@router.get("/google/callback")
async def google_callback(request: Request):
    """Process login response from Google and return user info"""
    user_google = await google_sso.verify_and_process(request)

    user: User = users_api.general_get(email=user_google.email)
    if not user:
        user = users_api.createAUX(user_google.username, user_google.email)

    redirect: RedirectResponse = RedirectResponse(base_url)
    redirect.set_cookie("user_id", user["id"])
    return redirect

@router.get("/logout")
def logout():
    response = RedirectResponse(base_url)
    response.delete_cookie("user_id")
    return response