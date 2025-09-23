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
    if not obj: raise HTTPException(404, "Assessment not found")
    return obj

@app.put("/assessments/{aid}", response_model=schemas.AssessmentOut)
def update_assessment(aid: int, payload: schemas.AssessmentUpdate, session: Session = Depends(get_db)):
    obj = session.get(models.Assessment, aid)
    if not obj: raise HTTPException(404, "Assessment not found")
    for k, v in payload.dict(exclude_unset=True).items():
        setattr(obj, k, v)
    session.commit(); session.refresh(obj); return obj

@app.delete("/assessments/{aid}")
def delete_assessment(aid: int, session: Session = Depends(get_db)):
    obj = session.get(models.Assessment, aid)
    if not obj: raise HTTPException(404, "Assessment not found")
    session.delete(obj); session.commit(); return {"ok": True}


