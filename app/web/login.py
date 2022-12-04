from fastapi import APIRouter, Request, Cookie, Depends, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from ..entities import users as users_api
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.hash import sha256_crypt
from ..entities.models import *


router = APIRouter()

#PATRON SINGLETON
class Singleton (object):

    class __Singleton :
        def __init__(self):
            self.user = None

        def __user__(self):
            return self.user

    instance = None

    def __new__(cls):
        if not Singleton.instance:
            Singleton.instance = Singleton.__Singleton()
        return Singleton.instance

templates = Jinja2Templates(directory="templates")

#OAUTH2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')

async def authenticate_user(email: str, password: str):
    userl = users_api.general_get(None,email)
    if len(userl) == 0:
        return False 

    user = userl[0]
    if not verify_password(user , password):
        return False
    return user["id"]

def verify_password(user:users_api.User, password:str):
    return sha256_crypt.verify(password, user["password_hash"])
    #return (password == user.pop("password_hash"))


async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        user = token
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail='Invalid username or password'
        )
    finally:
        login(Request,None)

    return await users_api.get_by_id(user)

@router.get("/", response_class=HTMLResponse)
def login(request: Request,err = Cookie(default=None)):
    return templates.TemplateResponse("login.html", {"request": request, "err":err})

@router.post("/register", response_class=HTMLResponse)
def create_user(request: Request, username: str = Form(), correo: str = Form(), password: str = Form()):
    try:
       users_api.create(username,correo,password)
        # user: UserPost = UserPost(username=username,email=email,password_hash=password)
    except HTTPException as e:
        return login(request, e.detail)

    return login(request,"Usuario registrado con exito")

@router.get("/logout", response_class=HTMLResponse)
def logout(request: Request,err = Cookie(default=None)):
    salida = Singleton()
    salida.user=None
    return templates.TemplateResponse("login.html", {"request": request, "err":err})

@router.post('/token')
async def generate_token(request: Request,form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        return login(request,"Usuario o contraseña no validos")

    singleton = Singleton()
    singleton.user = user
    return RedirectResponse("/houses", status_code=status.HTTP_303_SEE_OTHER)

def check_user():
    session = Singleton()
    if session.user is None:
        raise HTTPException(status_code=401, detail="No se ha iniciado sesión.")
    return session.user