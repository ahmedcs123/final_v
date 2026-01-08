from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
from . import schemas, database, models
from sqlalchemy.orm import Session

# Configuration
SECRET_KEY = "supersecretkey" # Change in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Database Auth
def authenticate_user(db: Session, username: str, password: str):
    user = db.query(models.Admin).filter(models.Admin.username == username).first()
    if not user:
        return False
    if not verify_password(password, user.password_hash):
        return False
    return user

def create_super_admin_if_not_exists(db: Session):
    # Check if any admin exists
    admin = db.query(models.Admin).first()
    if not admin:
        # Create Super Admin
        password_hash = get_password_hash("DesignMaster2025")
        new_admin = models.Admin(username="owner", password_hash=password_hash, role="super_admin")
        db.add(new_admin)
        db.commit()
        db.refresh(new_admin)
        print("Super Admin created: owner / DesignMaster2025")

async def get_current_user(request: Request, db: Session = Depends(database.get_db)):
    token = request.cookies.get("access_token")
    if not token:
        # Check Authorization header as fallback
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
    
    if not token:
        return None

    try:
        # Handle "Bearer <token>" format if present in cookie
        if token.startswith("Bearer "):
            token = token.split(" ")[1]
            
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        token_data = schemas.TokenData(username=username)
    except JWTError:
        return None
        
    user = db.query(models.Admin).filter(models.Admin.username == token_data.username).first()
    if user is None:
        return None
    return user

async def get_current_active_superuser(current_user: models.Admin = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    if current_user.role != "super_admin":
        raise HTTPException(status_code=403, detail="Not enough privileges")
    return current_user

def login_required(user: Optional[models.Admin] = Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return user
