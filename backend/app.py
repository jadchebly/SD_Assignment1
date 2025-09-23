from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from . import models, schemas, calculations, db

app = FastAPI(title="Grade & What-If Tracker", version="1.0")
# Allow local dev from any origin (tighten for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Create DB tables at startup (SQLite)
models.Base.metadata.create_all(bind=db.engine)

def get_db():
    session = db.SessionLocal()
    try:
        yield session
    finally:
        session.close()
