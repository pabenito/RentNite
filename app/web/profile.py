from fastapi import APIRouter, Request, Cookie, Form, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from ..entities import users as users_api
from ..entities import ratings as ratings_api
from app.entities import models
from app.web import login as login_api
import cloudinary
import cloudinary.uploader
from passlib.hash import sha256_crypt



router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
def perfil_usuario(request: Request):
    user = __check_user()
    return templates.TemplateResponse("profile.html", {"request": request, "user": users_api.get_by_id(user), "rating": ratings_api.get(None, user, None, None, None, None, None), "identificador": user, "perfil": user})

@router.get("/edit", response_class=HTMLResponse)
def edit(request: Request, error: str = ""):
    user = __check_user()
    return templates.TemplateResponse("profile.html", {"request": request, "user": users_api.get_by_id(user), "rating": ratings_api.get(None, user, None, None, None, None, None), "identificador": user, "editable": True, "error": error})

@router.get("/{id}", response_class=HTMLResponse)
def perfil_usuario_distinto(request: Request, id: str):
    user = __check_user()

    user_ratings = ratings_api.get(rater_id = user, rated_user_id = id)
    user_can_rate = len(user_ratings) == 0

    return templates.TemplateResponse("profile.html", {"request": request, "user": users_api.get_by_id(id), "rating": ratings_api.get(None, id, None, None, None, None, None), "identificador": user, "perfil": id, "user_can_rate": user_can_rate})


@router.post("/{id}/addRate", response_class=HTMLResponse)
def add_Rate(request: Request, id: str, estrellas: int = Form()):
    user = __check_user()

    ratings_api.create(user, id, None, estrellas)

    return perfil_usuario_distinto(request, id)

@router.get("/{id}/deleteRate/{rate_id}", response_class = HTMLResponse)
def delete_rating(request: Request, id: str, rate_id: str):
    __check_user()

    ratings_api.delete(rate_id)

    return perfil_usuario_distinto(request, id)

@router.post("/uploadPhoto", response_class=HTMLResponse)
def upload_photo(request: Request, file: UploadFile = File(...)):
    user = __check_user()

    user_class = users_api.get_by_id(user)

    if user_class["photo"] != "":
        #Take photo's url and get name of file to delete
        name =  user_class["photo"].split("/")
        name =  name[7]
        size = len(name)
        name = name[:size-4]

        #Delete photo from cloudinary
        cloudinary.uploader.destroy(name)
    
    #Upload photo to cloudinary
    result = cloudinary.uploader.upload(file.file)
    url = result.get("url")
    users_api.update(id=user,photo=url)
    
    return perfil_usuario(request)

@router.post("/save", response_class=HTMLResponse)
def save(request: Request, password: str = Form(), username: str = Form(), email: str = Form()):
    user = __check_user()
    try:
        users_api.update(id=user, username=username,
                        email=email, password=password)
        return perfil_usuario(request)
    except HTTPException as e:
        return edit(request, e.detail)

# Private methods

def __check_user():
    session = login_api.Singleton()
    if session.user is None:
        raise HTTPException(
            status_code=401, detail="No se ha iniciado sesión.")
    return session.user