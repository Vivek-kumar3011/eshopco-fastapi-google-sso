from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, JSONResponse
from authlib.integrations.starlette_client import OAuth
from starlette.middleware.sessions import SessionMiddleware
import os

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="your-random-secret-key")

oauth = OAuth()
oauth.register(
    name='google',
    client_id=os.getenv("CLIENT_ID"),
    client_secret=os.getenv("CLIENT_SECRET"),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'},
)

@app.get("/")
async def home(request: Request):
    user = request.session.get("user")
    if user:
        return {"message": "Logged in", "user": user}
    return RedirectResponse("/login")

@app.get("/login")
async def login(request: Request):
    redirect_uri = request.url_for("auth")
    return await oauth.google.authorize_redirect(request, redirect_uri)

@app.get("/auth")
async def auth(request: Request):
    token = await oauth.google.authorize_access_token(request)
    user = token.get("userinfo")
    request.session["user"] = user
    request.session["id_token"] = token.get("id_token")
    return RedirectResponse("/id_token")

@app.get("/id_token")
async def id_token(request: Request):
    id_token = request.session.get("id_token")
    return JSONResponse({"id_token": id_token})
