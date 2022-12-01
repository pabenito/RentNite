from fastapi import APIRouter, Request, Cookie, Depends, Form, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from ..entities import users as users_api
from .profile import perfil_usuario
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.hash import bcrypt

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
    user = userl[0]
    if not user:
        return False 
    if not verify_password(user , password):
        return False
    return user.pop("id")

def verify_password(user:users_api.User, password:str):
    #  return bcrypt.verify(password, user.password_hash)
    return (password == user.pop("password_hash"))


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



