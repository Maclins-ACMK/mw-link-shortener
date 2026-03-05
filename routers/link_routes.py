from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
import string
import random

from database import SessionLocal
from models import Link, User
from schemas import CreateLinkRequest
from core.config import SECRET_KEY, ALGORITHM
from core.limiter import limiter   # Safe because limiter defined before routers included

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# -------------------------
# Database Dependency
# -------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -------------------------
# Short Code Generator
# -------------------------
def generate_short_code(length: int = 6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


def generate_unique_code(db: Session, length: int = 6):
    while True:
        code = generate_short_code(length)
        exists = db.query(Link).filter(Link.short_code == code).first()
        if not exists:
            return code


# -------------------------
# Auth Dependency
# -------------------------
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")

        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.email == email).first()

    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    return user


# -------------------------
# Create Link (Rate Limited + Free Plan Limit)
# -------------------------
BASE_URL = "https://mw-link-shortener.onrender.com"

@router.post("/links")
def create_link(
    data: CreateLinkRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    short_code = generate_short_code()

    new_link = Link(
        original_url=data.original_url,
        short_code=short_code,
        owner_id=current_user.id
    )

    db.add(new_link)
    db.commit()
    db.refresh(new_link)

    return {
        "short_url": f"{BASE_URL}/{short_code}"
    }


# -------------------------
# Get My Links
# -------------------------
@router.get("/my-links")
def get_my_links(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    links = db.query(Link).filter(
        Link.owner_id == current_user.id
    ).all()

    return links


# -------------------------
# Redirect + Click Tracking
# -------------------------
@router.get("/{short_code}")
def redirect(short_code: str, db: Session = Depends(get_db)):
    link = db.query(Link).filter(
        Link.short_code == short_code
    ).first()

    if not link:
        raise HTTPException(status_code=404, detail="Link not found")

    # Increment clicks safely
    link.clicks += 1
    db.commit()

    return RedirectResponse(link.original_url)


# -------------------------
# Analytics
# -------------------------
@router.get("/analytics/{short_code}")
def get_link_analytics(
    short_code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    link = db.query(Link).filter(
        Link.short_code == short_code,
        Link.owner_id == current_user.id
    ).first()

    if not link:
        raise HTTPException(status_code=404, detail="Link not found")

    return {
        "original_url": link.original_url,
        "short_code": link.short_code,
        "clicks": link.clicks
    }