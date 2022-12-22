from fastapi import APIRouter, Request, Form, status, Cookie
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from typing import Union

from app.entities import chats as chats_api, messages as messages_api
from app.entities.models import MessageConstructor

# Create router
router = APIRouter()

# Create jinja templates
templates = Jinja2Templates(directory = "templates")

# API
@router.get("/")
def html(request: Request, user_id: Union[str, None] = Cookie(default=None)):
    chats: list = chats_api.get_by_user_id(user_id)
    if user_id is None:
        return RedirectResponse("/login")
    if chats == []:
        return templates.TemplateResponse("noChats.html", {"request": request})
    return templates.TemplateResponse("chats.html", {"request": request, "chats": chats, "user_id": user_id})

@router.get("/{chat_id}")
def html(request: Request, chat_id: str, user_id: Union[str, None] = Cookie(default=None)):
    return templates.TemplateResponse("chat.html", {"request": request, "chat_id": chat_id, "messages": messages_api.get(chat_id=chat_id) })

@router.post("/")
def html(request: Request, chat_id:str = Form(), message: str = Form(), user_id: Union[str, None] = Cookie(default=None)):
    new_message : MessageConstructor = MessageConstructor()
    new_message.sender_id = user_id
    new_message.chat_id = chat_id
    new_message.message = message

    messages_api.post(new_message)
    
    return RedirectResponse(f"/chats/{chat_id}", status_code=status.HTTP_303_SEE_OTHER)