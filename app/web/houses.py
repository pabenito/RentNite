from fastapi import APIRouter, Request, Cookie, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from ..entities import houses as houses_api
from ..entities import messages as messages_api
from ..entities.models import MessagePost, MessageResponse

router = APIRouter()

templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
def read_item(request: Request):
    return templates.TemplateResponse("offeredHouses.html", {"request": request, "houses": houses_api.get()})

@router.get("/{id}", response_class=HTMLResponse)
def house_details(request: Request, id: str, user = Cookie(default=None)):
    return templates.TemplateResponse("houseDetails.html", {"request": request, "house": houses_api.get_by_id(id), 
                                                            "comments": messages_api.get(None, id, None, None, None), "user": user})

@router.post("/{id}/addComment", response_class=HTMLResponse)
def add_comment(request: Request, id: str, user = Cookie(default=None), comment: str = Form()):
    message: MessagePost = MessagePost(sender_id="636ad4aa5baf6bcddce08814", message=comment, house_id=id)
    messages_api.post(message)

    return house_details(request, id, user)