import cloudinary
import cloudinary.uploader
from os import environ
from fastapi import  File, UploadFile
from .entities import users as users_api

#Cloudinary configuration

cloudinary.config(
    cloud_name = environ["cloud_name"],
    api_key = environ["api_key"],
    api_secret = environ["api_secret"]
)

def get_photo_id(url:str):
    name =  url.split("/")
    name =  name[7]
    size = len(name)
    name = name[:size-4]
    return name

def delete_photo(name:str):
    cloudinary.uploader.destroy(name)

def upload_photo_user(user:str,file : UploadFile):
    result = cloudinary.uploader.upload(file.file)
    url = result.get("url")
    users_api.update(id=user,photo=url)

def upload_photo_house(file:UploadFile):
    result = cloudinary.uploader.upload(file.file)
    return result.get("url")
