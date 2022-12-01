from fastapi import APIRouter, Request, Cookie, Form, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse,RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from ..entities import users as users_api
from ..entities import ratings as ratings_api
from app.entities import models
from app.web import login as login_api
#from flickrapi import FlickrAPI

router = APIRouter()

templates = Jinja2Templates(directory="templates")

api_secret="d0009bb5d0d8f8f8"
api_key="b3b172dc37a0267d33cf70ee2d8303fc"
#flickr = FlickrAPI(api_key=api_key,secret=api_secret)


@router.get("/", response_class=HTMLResponse)
def perfil_usuario(request: Request):
    user = __chechUser()
    return templates.TemplateResponse("profile.html", {"request": request, "user": users_api.get_by_id(user), "rating": ratings_api.get(None, user, None, None, None, None, None), "identificador": user})

@router.get("/{id}", response_class=HTMLResponse)
def perfil_usuario_distinto(request: Request, id: str):
    user = __chechUser()
    return templates.TemplateResponse("profile.html", {"request": request, "user": users_api.get_by_id(id), "rating": ratings_api.get(None, id, None, None, None, None, None), "identificador": user, "perfil":id})

@router.post("/{id}/addRate", response_class=HTMLResponse)
def add_Rate(request: Request, id: str, estrellas: int = Form()):
    user = __chechUser()

    ratings_api.create(user, id, None, estrellas)

    return perfil_usuario(request)

@router.post("/{id}/uploadPhoto", response_class=HTMLResponse)
def upload_photo(request: Request, id: str, file: bytes = File()):
    user = __chechUser()

    #lickr.authenticate_via_browser
    #flickr.upload("perfil",fileobj=file,title="RentNitePrueba",is_public=1)

    return perfil_usuario(request)

@router.get("/{id}/edit", response_class=HTMLResponse)
def edit(request: Request, id: str):
    user = __chechUser()
    return templates.TemplateResponse("profile.html", {"request": request, "user": users_api.get_by_id(user), "rating": ratings_api.get(None, user, None, None, None, None, None), "identificador": user,"editable":True})

@router.post("/save", response_class=HTMLResponse)
def save(request: Request,password:str=Form(),username:str=Form(),email:str=Form()):
    user = __chechUser()

    users_api.update(id=user,username=username,email=email,password=password)
    
    return perfil_usuario(request)

# Private methods
def __chechUser():
    session = login_api.Singleton()
    if session.user is None:
        raise HTTPException(
            status_code=401, detail="No se ha iniciado sesión.")
    return session.user