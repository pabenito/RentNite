from fastapi import APIRouter, Request, Cookie, Depends, Form, HTTPException, status, Response, Body
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from ..entities import users as users_api
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.hash import sha256_crypt
from ..entities.models import *
from fastapi_sso.sso.google import GoogleSSO
from requests_futures.sessions import FuturesSession

router = APIRouter()

session: FuturesSession = FuturesSession()

base_url="http://127.0.0.1:8000"
headers = {"accept": "application/json", "Content-Type": "application/json"}

templates = Jinja2Templates(directory="templates")

# OAUTH2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


async def authenticate_user(email: str, password: str):
    user = users_api.general_get(email=email)
    if user is None:
        return False

    if not verify_password(user, password):
        return False
    return user["id"]


def verify_password(user: User, password: str):
    return sha256_crypt.verify(password, user["password_hash"])


def login_Google(email: str, username: str):
    user = users_api.general_get(email=email)
    if not user:
        user = users_api.createAUX(username, email)
    print(f"Hey, google callback. {base_url}/login/user user_id:{user['id']}")
    result = session.post(base_url + "/login/user", headers = headers, json={"user_id" : user["id"]}).result()
    print("End")
    return result

@router.get("/", response_class=HTMLResponse)
def login(request: Request, login_error: str = "", registration_error: str = "", registration_success_message: str = ""):
    return templates.TemplateResponse("login.html", {"request": request, "login_error": login_error, "registration_error": registration_error,
                                                     "registration_success_message": registration_success_message})

@router.post("/register", response_class=HTMLResponse)
def create_user(request: Request, username: str = Form(), correo: str = Form(), password: str = Form()):
    try:
       users_api.create(username, correo, password)
        # user: UserPost = UserPost(username=username,email=email,password_hash=password)
    except HTTPException as e:
        return login(request, registration_error=e.detail)

    return login(request, registration_success_message="Usuario registrado con exito")


@router.get("/logout", response_class=HTMLResponse)
def logout(request: Request):
    salida = Singleton()
    salida.user = None
    return RedirectResponse("/")

def get_user():
    user_id = session.get(base_url + "/login/user").result().json()
    print(user_id)
    return user_id

# Cookies

@router.post('/token')
async def generate_token(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        return login(request, "Usuario o contraseña no validos")
    result = session.post(base_url + "/login/user", data={"user_id":user.id}).result()
    return RedirectResponse("/houses", status_code=status.HTTP_303_SEE_OTHER)
    return result

@router.post('/user')
async def post_user_id(response: Response, user_id: Union[str, None] = Body(default=None)):
    print(f"Hey, post {user_id}")
    response.set_cookie("user_id", user_id)
    return user_id

@router.get('/user')
def get_user_id(user_id: Union[str, None] = Cookie(default=None)):
    print("get user cookie")
    return user_id