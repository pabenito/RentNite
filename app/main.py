# Import libraries
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.web import login
from fastapi.responses import RedirectResponse
from starlette.config import Config
from authlib.integrations.starlette_client import OAuth
import config


# Import modules
from .entities import router as entities
from .opendata import router as opendata
from .web import router as web

# Create app
app = FastAPI()

# # OAuth settings
# GOOGLE_CLIENT_ID = config.GOOGLE_CLIENT_ID or None
# GOOGLE_CLIENT_SECRET = config.GOOGLE_CLIENT_SECRET or None
# if GOOGLE_CLIENT_ID is None or GOOGLE_CLIENT_SECRET is None:
#     raise BaseException('Missing env variables')

# # Set up oauth
# config_data = {'GOOGLE_CLIENT_ID': GOOGLE_CLIENT_ID, 'GOOGLE_CLIENT_SECRET': GOOGLE_CLIENT_SECRET}
# starlette_config = Config(environ=config_data)
# oauth = OAuth(starlette_config)
# oauth.register(
#     name='google',
#     server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
#     client_kwargs={'scope': 'openid email profile'},
# )

# from starlette.middleware.sessions import SessionMiddleware
# SECRET_KEY = config.SECRET_KEY or None
# if SECRET_KEY is None:
#     raise 'Missing SECRET_KEY'
# app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

# from fastapi import Request
# from starlette.responses import RedirectResponse
# from authlib.integrations.starlette_client import OAuthError

# @app.route('/login')
# async def login(request: Request):
#     redirect_uri = request.url_for('auth')  # This creates the url for the /auth endpoint
#     return await oauth.google.authorize_redirect(request, redirect_uri)


# @app.route('/auth')
# async def auth(request: Request):
#     try:
#         access_token = await oauth.google.authorize_access_token(request)
#         print(access_token)
#         print("funciona")
#     except OAuthError:
#         return RedirectResponse(url='/')
#     user_data = await oauth.google.parse_id_token(request, access_token)
#     request.session['user'] = dict(user_data)
#     return RedirectResponse(url='/')

# from starlette.responses import HTMLResponse
# @app.get('/')
# def public(request: Request):
#     user = request.session.get('user')
#     if user:
#         name = user.get('name')
#         return HTMLResponse(f'<p>Hello {name}!</p><a href=/logout>Logout</a>')
#     return HTMLResponse('<a href=/login>Login</a>')


# @app.route('/logout')
# async def logout(request: Request):
#     request.session.pop('user', None)
#     return RedirectResponse(url='/')

# from starlette.requests import Request

# @app.get("/login/google")
# async def login_via_google(request: Request):
#     redirect_uri = request.url_for('auth_via_google')
#     return await oauth.google.authorize_redirect(request, redirect_uri)

# @app.get("/auth/google")
# async def auth_via_google(request: Request):
#     token = await oauth.google.authorize_access_token(request)
#     user = token['userinfo']
#     return dict(user)

"""This is an example usage of fastapi-sso.
"""

from fastapi import FastAPI, Request
from fastapi_sso.sso.google import GoogleSSO


google_sso = GoogleSSO(
    config.GOOGLE_CLIENT_ID,
    config.GOOGLE_CLIENT_SECRET,
    "http://127.0.0.1:8000/google/callback"
)


@app.get("/google/login")
async def google_login():
    """Generate login url and redirect"""
    return await google_sso.get_login_redirect()


@app.get("/google/callback")
async def google_callback(request: Request):
    """Process login response from Google and return user info"""
    user = await google_sso.verify_and_process(request)
    return {
        "id": user.id,
        "picture": user.picture,
        "display_name": user.display_name,
        "email": user.email,
    }



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
    return RedirectResponse("/login")
