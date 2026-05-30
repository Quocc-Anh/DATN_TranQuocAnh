import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.database import Base, engine
from app.routers import auth, chat, classrooms, lessons, reviews

Base.metadata.create_all(bind=engine)

app = FastAPI(title="E-Learning API", version="0.3.0")

origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

AVATAR_DIR = os.path.join("data", "avatars")
os.makedirs(AVATAR_DIR, exist_ok=True)
app.mount(
    "/uploads/avatars",
    StaticFiles(directory=AVATAR_DIR),
    name="avatars",
)

app.include_router(auth.router)
app.include_router(classrooms.router)
app.include_router(reviews.router)
app.include_router(lessons.router)
app.include_router(chat.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
