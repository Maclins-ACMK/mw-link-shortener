from fastapi import FastAPI
from database import engine
from models import Base

from routers.auth_routes import router as auth_router
from routers.link_routes import router as link_router

app = FastAPI()

# Create database tables
Base.metadata.create_all(bind=engine)

app.include_router(auth_router)
app.include_router(link_router)

@app.get("/")
def home():
    return {
        "service": "MW Link Shortener API",
        "status": "running",
        "docs": "https://mw-link-shortener.onrender.com/docs"
    }