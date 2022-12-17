import cloudinary
import cloudinary.uploader
import config
from fastapi import  File, UploadFile
from .entities import users as users_api

#Cloudinary configuration

cloudinary.config(
    cloud_name = config.cloud_name,
    api_key = config.api_key,
    api_secret = config.api_secret
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
