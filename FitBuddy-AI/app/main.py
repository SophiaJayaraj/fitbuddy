from contextlib import asynccontextmanager

from fastapi import FastAPI

from fastapi.staticfiles import StaticFiles

from .database import init_db

from .routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):

    # Create database tables
    init_db()

    yield


app = FastAPI(

    title="FitBuddy – AI Fitness Plan Generator",

    description=(
        "AI-powered fitness and wellness "
        "plan generator using FastAPI, "
        "Gemini and SQLite."
    ),

    version="1.0.0",

    lifespan=lifespan,
)


# Static files
app.mount(
    "/static",
    StaticFiles(
        directory="static"
    ),
    name="static",
)


# Routes
app.include_router(
    router
)