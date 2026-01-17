from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.schemas.user import HistoryCreate, HistoryUpdate
from app.services.history_service import HistoryService
from app.core.database import SessionLocal
from datetime import datetime

router = APIRouter(prefix="/history", tags=["History"])
service = HistoryService()

# ---------------------------
# DB bağlantısı
# ---------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------------------
# CREATE
# ---------------------------
@router.post("/")
def create_history(history: HistoryCreate, db: Session = Depends(get_db)):
    if history.answered_at is None:
        history.answered_at = datetime.utcnow()
    return service.create(db, history)

# ---------------------------
# GET ALL
# ---------------------------
@router.get("/")
def get_all_history(db: Session = Depends(get_db)):
    return service.get_all(db)

# ---------------------------
# GET BY STUDENT ID
# ---------------------------
@router.get("/student/{student_id}")
def get_history_by_student(student_id: int, db: Session = Depends(get_db)):
    records = service.get_by_student(db, student_id)
    if not records:
        raise HTTPException(status_code=404, detail="No history found for this student")
    return records

# ---------------------------
# GET BY STUDENT EMAIL
# ---------------------------
@router.get("/by-email")
def get_histories_by_email(email: str = Query(..., description="Student email"), db: Session = Depends(get_db)):
    histories = service.get_by_student_email(db, email)
    if not histories:
        raise HTTPException(status_code=404, detail="No history found for this email")
    return histories

# ---------------------------
# GET BY HISTORY ID
# ---------------------------
@router.get("/{history_id}")
def get_history(history_id: int, db: Session = Depends(get_db)):
    history = service.get(db, history_id)
    if not history:
        raise HTTPException(status_code=404, detail="History not found")
    return history

# ---------------------------
# UPDATE
# ---------------------------
@router.put("/{history_id}")
def update_history(history_id: int, history: HistoryUpdate, db: Session = Depends(get_db)):
    updated = service.update(db, history_id, history)
    if not updated:
        raise HTTPException(status_code=404, detail="History not found")
    return updated

# ---------------------------
# DELETE
# ---------------------------
@router.delete("/{history_id}")
def delete_history(history_id: int, db: Session = Depends(get_db)):
    deleted = service.delete(db, history_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="History not found")
    return {"detail": "History deleted"}
