from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from . import db, models, schemas, calculations

app = FastAPI(title="Grade & What-If Tracker", version="1.0")

# CORS so the static frontend can call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for local dev; tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables on startup (SQLite)
models.Base.metadata.create_all(bind=db.engine)


def get_db():
    session = db.SessionLocal()
    try:
        yield session
    finally:
        session.close()


@app.get("/health")
def health():
    return {"ok": True}

# ---- CRUD: Assessments -------------------------------------------------------

@app.post("/assessments", response_model=schemas.AssessmentOut)
def create_assessment(payload: schemas.AssessmentIn, session: Session = Depends(get_db)):
    obj = models.Assessment(**payload.dict())
    session.add(obj)
    session.commit()
    session.refresh(obj)
    return obj


@app.get("/assessments", response_model=list[schemas.AssessmentOut])
def list_assessments(session: Session = Depends(get_db)):
    return session.query(models.Assessment).order_by(models.Assessment.due_date).all()


@app.get("/assessments/{aid}", response_model=schemas.AssessmentOut)
def get_assessment(aid: int, session: Session = Depends(get_db)):
    obj = session.get(models.Assessment, aid)
    if not obj:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return obj


@app.put("/assessments/{aid}", response_model=schemas.AssessmentOut)
def update_assessment(aid: int, payload: schemas.AssessmentUpdate, session: Session = Depends(get_db)):
    obj = session.get(models.Assessment, aid)
    if not obj:
        raise HTTPException(status_code=404, detail="Assessment not found")
    for k, v in payload.dict(exclude_unset=True).items():
        setattr(obj, k, v)
    session.commit()
    session.refresh(obj)
    return obj


@app.delete("/assessments/{aid}")
def delete_assessment(aid: int, session: Session = Depends(get_db)):
    obj = session.get(models.Assessment, aid)
    if not obj:
        raise HTTPException(status_code=404, detail="Assessment not found")
    session.delete(obj)
    session.commit()
    return {"ok": True}

# ---- Stats: current / what-if / validate ------------------------------------

@app.get("/stats/current", response_model=schemas.CurrentStats)
def current_stats(session: Session = Depends(get_db)):
    rows = session.query(models.Assessment).all()
    return calculations.current_stats(rows)


@app.get("/stats/what-if", response_model=schemas.WhatIf)
def what_if(target: float, session: Session = Depends(get_db)):
    rows = session.query(models.Assessment).all()
    return calculations.what_if(rows, target)


@app.get("/stats/validate", response_model=schemas.Validation)
def validate_weights(session: Session = Depends(get_db)):
    rows = session.query(models.Assessment).all()
    return calculations.validate_weights(rows)
