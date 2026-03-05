from fastapi import FastAPI
from slowapi.middleware import SlowAPIMiddleware

from core.limiter import limiter
from routers.auth_routes import router as auth_router
from routers.link_routes import router as link_router

app = FastAPI()

app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

app.include_router(auth_router)
app.include_router(link_router)