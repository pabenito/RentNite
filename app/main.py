# Import libraries
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.web import login
from fastapi.responses import RedirectResponse


# Import modules
from .entities import router as entities
from .opendata import router as opendata
from .web import router as web

# Create app
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
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
    tags=["entities"]
)

app.include_router(
    web.router,
    tags=["web"]
)

#oauth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


@app.get("/")
async def root():
    return RedirectResponse("/login")

@app.post('/token')
async def generate_token(request: Request,form_data: OAuth2PasswordRequestForm = Depends()):
    user = await login.authenticate_user(form_data.username, form_data.password)
    if not user:
        return login.login(request,"Usuario o contraseña no validos")

    singleton = login.Singleton()
    singleton.user = user
    return RedirectResponse("/houses", status_code=status.HTTP_303_SEE_OTHER)
