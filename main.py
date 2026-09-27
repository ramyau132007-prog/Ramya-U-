"""
main.py
FastAPI entry point for FitBuddy — AI Fitness Plan Generator using Gemini Models.

Run with:
    uvicorn app.main:app --reload

Then visit:
    http://127.0.0.1:8000        (app)
    http://127.0.0.1:8000/docs   (interactive API docs)
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.database import init_db
from app.routes import router

app = FastAPI(title="FitBuddy - AI Fitness Plan Generator")

# Serve static assets (images, etc.)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Register all routes
app.include_router(router)


@app.on_event("startup")
def on_startup():
    init_db()
