from typing import List, Union
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Request, Form, Cookie, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.encoders import jsonable_encoder
from os import environ

import json

from app.entities import chats as chats_api, messages as messages_api
from app.entities.models import MessageConstructor, Message

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

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@router.get("/{chat_id}")
async def html(request: Request, chat_id:str, user_id: Union[str, None] = Cookie(default=None)):
    return templates.TemplateResponse("chat.html", {"request": request, "chat_id": chat_id, "messages": messages_api.get(chat_id=chat_id), "user_id": user_id, "ip": environ["ip"]})

@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            data = json.loads(data)
            new_message = post(chat_id=data["chat_id"], message=data["message"], user_id=data["user_id"])
            check_image(new_message)
            print(new_message)
            await manager.broadcast(json.dumps(new_message, default=str))
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print(f"Client #{client_id} left the chat")

def post(chat_id:str, message: str, user_id: str):
    new_message : MessageConstructor = MessageConstructor()
    new_message.sender_id = user_id
    new_message.chat_id = chat_id
    new_message.message = message
    return messages_api.post(new_message)

def check_image(message: dict):
    if message["photo"] is None or message["photo"] == "":
        message["photo"] = "https://cdn.onlinewebfonts.com/svg/img_103581.png"