from fastapi import APIRouter, Request, Cookie, Form, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from ..entities import users as users_api
from ..entities import ratings as ratings_api
from app.entities import models
from app.web import login
from passlib.hash import sha256_crypt
from .. import cloudinary as cloud
from datetime import datetime, date, time
from pytz import timezone



router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
def perfil_usuario(request: Request):
    user = login.get_user()
    print(request)
    print(users_api.get_by_id(user))
    if user is None:
        return login.redirect()

    return templates.TemplateResponse("profile.html", {"request": request, "user": users_api.get_by_id(user), "rating": ratings_api.get(None, user, None, None, None, None, None), "user_id": user, "perfil": user})

@router.get("/edit", response_class=HTMLResponse)
def edit(request: Request, error: str = ""):
    user = login.get_user()
    if user is None:
        return login.redirect()

    return templates.TemplateResponse("profile.html", {"request": request, "user": users_api.get_by_id(user), "rating": ratings_api.get(None, user, None, None, None, None, None), "user_id": user, "editable": True, "error": error})

@router.get("/{id}", response_class=HTMLResponse)
def perfil_usuario_distinto(request: Request, id: str):
    user = login.get_user()

    if user is None:
        user_can_rate = True
    else:
        user_ratings = ratings_api.get(rater_id = user, rated_user_id = id)
        user_can_rate = len(user_ratings) == 0

    return templates.TemplateResponse("profile.html", {"request": request, "user": users_api.get_by_id(id), "rating": ratings_api.get(None, id, None, None, None, None, None), "user_id": user, "perfil": id, "user_can_rate": user_can_rate})


@router.post("/{id}/addRate", response_class=HTMLResponse)
def add_Rate(request: Request, id: str, estrellas: int = Form(), comment =Form()):
    user = login.get_user()
    if user is None:
        return login.redirect()

    date = datetime.now(timezone("Europe/Madrid"))
    rt : models.RatingPost = models.RatingPost(rater_id=user ,date=date,rated_user_id=id,
                                               rated_user_Name=None,rated_house_id=None,rate=estrellas,comment=comment)
    ratings_api.create(rt)

    return perfil_usuario_distinto(request, id)

@router.get("/{id}/deleteRate/{rate_id}", response_class = HTMLResponse)
def delete_rating(request: Request, id: str, rate_id: str):
    user = login.get_user()
    if user is None:
        return login.redirect()

    ratings_api.delete(rate_id)

    return perfil_usuario_distinto(request, id)

@router.post("/uploadPhoto", response_class=HTMLResponse)
def upload_photo(request: Request, file: UploadFile = File(...)):
    user = login.get_user()
    if user is None:
        return login.redirect()

    user_class = users_api.get_by_id(user)

    if user_class["photo"] != "":
        #Take photo's url and get name of file to delete
        name = cloud.get_photo_id(url=user_class["photo"])

        #Delete photo from cloudinary
        cloud.delete_photo(name=name)
        

    
    #Upload photo to cloudinary
    cloud.upload_photo_user(user=user,file=file)
    
    return perfil_usuario(request)

@router.post("/save", response_class=HTMLResponse)
def save(request: Request,newpassword: str = Form(), password: str = Form(), username: str = Form(), email: str = Form()):
    user = login.get_user()
    if user is None:
        return login.redirect()

    user_object : models.User = users_api.get_by_id(user)
    try:
        if login.verify_password(user=user_object,password=password):
            users_api.update(id=user, username=username,
                        email=email, password=newpassword)
            return perfil_usuario(request)
        else:
            return edit(request,"Contraseña antigua mal introducida")
    except HTTPException as e:
        return edit(request, e.detail)
    
@router.post("/saveGoogle", response_class=HTMLResponse)
def save_Google(request: Request,username: str = Form()):
    user = login.get_user()
    if user is None:
        return login.redirect()
    try:
        users_api.update(id=user, username=username)
        return perfil_usuario(request)
    except HTTPException as e:
        return edit(request, e.detail)