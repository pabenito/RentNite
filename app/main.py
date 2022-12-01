# Import libraries
from fastapi import FastAPI, Depends, HTTPException, status, Request, Response, Cookie
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.web import login
from app.web import profile
from app.web import cookies
from fastapi.responses import RedirectResponse

# Import modules
from .entities import router as entities
from .opendata import router as opendata
from .web import router as web

base_url = "http://127.0.0.1:8000"

# Create app
app = FastAPI()

# cors
origins = [
    "http://i.imgur.com",
    "https://i.imgur.com",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:8000/houses/#loaded"
    "https://127.0.0.1:8000",
    "https://127.0.0.1:8000/houses/#loaded"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# Include modules
app.include_router(
    opendata.router,
    prefix="/opendata",
    tags=["opendata"]
)

app.include_router(
    entities.router,
    prefix="/entities",
    tags=["entities"],

)

app.include_router(
    web.router,
    tags=["web"],

)

#oauth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


@app.get("/")
async def root(token: str = Depends(oauth2_scheme)):
    return {"the_token": token}


@app.post('/token')
async def generate_token(response: Response ,form_data: OAuth2PasswordRequestForm = Depends()):
    user = await login.authenticate_user(form_data.username, form_data.password)
    if not user:
        return login.login("Usario o contraseña no validos")
        
    response.set_cookie(key="user", value=user)
    return RedirectResponse(base_url + "/profile")
