# Import libraries
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.web import login
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
from os import environ


# Import modules
from app.entities import router as entities
from app.opendata import router as opendata
from app.web import router as web

# Create app
app = FastAPI()

"""This is an example usage of fastapi-sso.
"""

from fastapi import FastAPI, Request
from fastapi_sso.sso.google import GoogleSSO


google_sso = GoogleSSO(
    environ["GOOGLE_CLIENT_ID"],
    environ["GOOGLE_CLIENT_SECRET"],
    environ["APP_URL"]
)


@app.get("/google/login")
async def google_login():
    """Generate login url and redirect"""
    return await google_sso.get_login_redirect()


@app.get("/google/callback")
async def google_callback(request: Request):
    """Process login response from Google and return user info"""
    user = await google_sso.verify_and_process(request)
    
    login.login_Google(user.email,user.display_name)
    return RedirectResponse("/houses", status_code=status.HTTP_303_SEE_OTHER)




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


@app.get("/")
async def root():
    return RedirectResponse("/houses")
