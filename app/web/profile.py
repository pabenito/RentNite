from fastapi import APIRouter, Request, Cookie, Form, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from ..entities import users as users_api
from ..entities import ratings as ratings_api
from app.entities import models
from app.web import login
from .. import cloudinary as cloud
from datetime import datetime
from pytz import timezone
from typing import Union


router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
def perfil_usuario(request: Request, user_id: Union[str, None] = Cookie(default=None)):
    user = user_id
    if user is None:
        return RedirectResponse("/login")

    return templates.TemplateResponse("profile.html", {"request": request, "user": users_api.get_by_id(user), "rating": ratings_api.get(None, user, None, None, None, None, None), "user_id": user, "perfil": user})

@router.get("/edit", response_class=HTMLResponse)
def edit(request: Request, error: str = "", user_id: Union[str, None] = Cookie(default=None)):
    user = user_id
    if user is None:
        return RedirectResponse("/login")

    return templates.TemplateResponse("profile.html", {"request": request, "user": users_api.get_by_id(user), "rating": ratings_api.get(None, user, None, None, None, None, None), "user_id": user, "editable": True, "error": error})

@router.get("/{id}", response_class=HTMLResponse)
def perfil_usuario_distinto(request: Request, id: str, user_id: Union[str, None] = Cookie(default=None)):
    user = user_id

    if user is None:
        user_can_rate = True
    else:
        user_ratings = ratings_api.get(rater_id = user, rated_user_id = id)
        user_can_rate = len(user_ratings) == 0

    return templates.TemplateResponse("profile.html", {"request": request, "user": users_api.get_by_id(id), "rating": ratings_api.get(None, id, None, None, None, None, None), "user_id": user, "perfil": id, "user_can_rate": user_can_rate})


@router.post("/{id}/addRate", response_class=HTMLResponse)
def add_Rate(request: Request, id: str, estrellas: int = Form(), comment =Form(), user_id: Union[str, None] = Cookie(default=None)):
    user = user_id
    if user is None:
        return RedirectResponse("/login", status_code = status.HTTP_302_FOUND)

    date = datetime.now(timezone("Europe/Madrid"))
    rt : models.RatingPost = models.RatingPost(rater_id=user ,date=date,rated_user_id=id,
                                               rated_user_Name=None,rated_house_id=None,rate=estrellas,comment=comment)
    ratings_api.create(rt)

    return perfil_usuario_distinto(request, id, user_id)

@router.get("/{id}/deleteRate/{rate_id}", response_class = HTMLResponse)
def delete_rating(request: Request, id: str, rate_id: str, user_id: Union[str, None] = Cookie(default=None)):
    user = user_id
    if user is None:
        return RedirectResponse("/login")

    ratings_api.delete(rate_id)

    return perfil_usuario_distinto(request, id, user_id)

@router.post("/uploadPhoto", response_class=HTMLResponse)
def upload_photo(request: Request, file: UploadFile = File(...), user_id: Union[str, None] = Cookie(default=None)):
    user = user_id
    if user is None:
        return RedirectResponse("/login", status_code = status.HTTP_302_FOUND)

    user_class = users_api.get_by_id(user)

    if user_class["photo"] != "":
        #Take photo's url and get name of file to delete
        name = cloud.get_photo_id(url=user_class["photo"])

        #Delete photo from cloudinary
        cloud.delete_photo(name=name)
        

    
    #Upload photo to cloudinary
    cloud.upload_photo_user(user=user,file=file)
    
    return perfil_usuario(request, user)

@router.post("/save", response_class=HTMLResponse)
def save(request: Request,newpassword: str = Form(), password: str = Form(), username: str = Form(), email: str = Form(), user_id: Union[str, None] = Cookie(default=None)):
    user = user_id
    if user is None:
        return RedirectResponse("/login", status_code = status.HTTP_302_FOUND)
    
    user_object : models.User = users_api.get_by_id(user)
    try:
        if login.verify_password(user=user_object,password=password):
            users_api.update(id=user, username=username,
                        email=email, password=newpassword)
            return perfil_usuario(request, user)
        else:
            return edit(request,"Contraseña antigua mal introducida", user)
    except HTTPException as e:
        return edit(request, e.detail, user)
    
@router.post("/saveGoogle", response_class=HTMLResponse)
def save_Google(request: Request,username: str = Form(), user_id: Union[str, None] = Cookie(default=None)):
    user = user_id
    if user is None:
        return RedirectResponse("/login", status_code = status.HTTP_302_FOUND)
    try:
        users_api.update(id=user, username=username)
        return perfil_usuario(request, user)
    except HTTPException as e:
        return edit(request, e.detail, user)