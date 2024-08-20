import base64
from typing import Annotated
from PIL import Image
from io import BytesIO
from pathlib import Path

from datetime import timedelta
from fastapi import FastAPI, HTTPException, Depends, status, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse, JSONResponse
from starlette.middleware.sessions import SessionMiddleware
from authlib.integrations.starlette_client import OAuth, OAuthError
from sqlalchemy.orm import Session
from .database import Base, engine, SessionLocal
from .models import QRCodeHistory
from .crud import get_user_by_email, create_user
from .schemas import UserCreate, Token, QRCodeHistoryCreate
from .auth import authenticate_user, create_access_token, verify_token, ACCESS_TOKEN_EXPIRE_MINUTES
from .config import CLIENT_ID, CLIENT_SECRET, ENVIRONMENT, SESSION_SECRET_KEY
from fastapi.staticfiles import StaticFiles

app = FastAPI()

if ENVIRONMENT != "production":
    Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine, checkfirst=True)

origins = ["http://localhost:8000", "http://ec2-3-27-223-46.ap-southeast-2.compute.amazonaws.com"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET_KEY)
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

oauth = OAuth()
oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    client_kwargs={
        'scope': 'openid email profile',
        'redirect_uri': 'http://localhost:8000/auth'
    }
)

templates = Jinja2Templates(directory="frontend/templates")

# Dependency
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

@app.get("/")
def index(request: Request):
    user = request.session.get('user')
    if user:
        return RedirectResponse('/qrcode')
    return templates.TemplateResponse(name="home.html",context={"request": request})

@app.get('/qrcode')
def qrcode(request: Request):
    user = request.session.get('user')
    if not user:
        return RedirectResponse('/')
    return templates.TemplateResponse(name='qrcode.html', context={'request': request, 'user': user})

@app.get('/register')
def register(request: Request):
    user = request.session.get('user')
    return templates.TemplateResponse('register.html', {'request': request})

@app.post("/register")
def register_user(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    db_user = get_user_by_email(db, email=email)
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    user_create = UserCreate(email=email, password=password)
    create_user(db=db, user=user_create)
    request.session['user'] = dict(user_create)
    # change status code 302 for GET request
    return RedirectResponse('/qrcode', status_code=status.HTTP_302_FOUND)

@app.post("/login")
def login_for_access_token(request: Request, email: Annotated[str, Form()], password: Annotated[str, Form()], db: Session = Depends(get_db)):
    user = authenticate_user(email, password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # generate access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user.email
        },
        expires_delta=access_token_expires
    )
    request.session['user'] = user
    return RedirectResponse('/qrcode', status_code=status.HTTP_302_FOUND)

@app.get("/verify-token/{token}")
async def verify_user_token(token: str):
    verify_token(token=token)
    return {"message": "Token is valid"}

@app.get("/login/google")
async def login(request: Request):
    redirect_uri = request.url_for('auth')
    return await oauth.google.authorize_redirect(request, redirect_uri)

@app.get('/auth')
async def auth(request: Request, db: Session = Depends(get_db)):
    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError as e:
        return JSONResponse(
            status_code=400,
            content={"detail": "Authentication failed. Please try again."}
        )
    user = token.get('userinfo')
    if user:
        email = user.get('email')
        db_user = get_user_by_email(db, email=email)
        if not db_user:
            create_user(db=db, user=UserCreate(email=email, password=None))
        
        # generate access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={
                "sub": user.email
            },
            expires_delta=access_token_expires
        )
        request.session['user'] = dict(user)
        return RedirectResponse('/qrcode')

    return JSONResponse(
        status_code=400,
        content={"detail": "User info is not available."}
    )

def save_qr_code_image(image_base64: str, filename: str):
    image_data = base64.b64decode(image_base64.split(',')[1])
    image = Image.open(BytesIO(image_data))
    image_path = Path('frontend/static/qr_code_downloaded') / filename
    image.save(image_path)

@app.post("/save_qr_history")
def save_qr_history(request: Request, qr_history: QRCodeHistoryCreate, db: Session = Depends(get_db)):
    user = request.session.get('user')
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    db_user = get_user_by_email(db, email=user.get('email'))
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    qr_code_image_base64 = qr_history.qr_code_image_base64
    qr_code_image_filename = qr_history.qr_code_image_filename

    # save QR Code image 
    if qr_code_image_base64:
        save_qr_code_image(qr_code_image_base64, qr_code_image_filename)

    qr_code_history = QRCodeHistory(
        text=qr_history.text,
        qr_code_image_filename=qr_code_image_filename,
        owner_id=db_user.id
    )
    db.add(qr_code_history)
    db.commit()
    db.refresh(qr_code_history)
    return {"message": "QR Code history saved", "qr_code_id": qr_code_history.id}
    
@app.get("/history")
def get_qr_history(request: Request, db: Session = Depends(get_db)):
    user = request.session.get('user')
    # print(user)
    if not user:
        return RedirectResponse('/')
    print(user.get("email"))
    db_user = get_user_by_email(db, email=user.get('email'))
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    qr_code_history = db.query(QRCodeHistory).filter(QRCodeHistory.owner_id == db_user.id).all()
    print(qr_code_history)
    return templates.TemplateResponse('history.html', {'request': request, 'history': qr_code_history})

@app.get('/logout')
def logout(request: Request):
    request.session.pop('user')
    request.session.clear()
    return RedirectResponse('/')