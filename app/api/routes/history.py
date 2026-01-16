from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.user import History
from app.schemas.user import HistoryCreate
from app.services.history_service import HistoryService
from app.core.database import SessionLocal
from datetime import datetime

router = APIRouter(prefix="/history", tags=["History"])
service = HistoryService()

# DB bağlantısı
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# CREATE
@router.post("/")
def create_history(history: HistoryCreate, db: Session = Depends(get_db)):
    # Eğer answered_at boş ise otomatik olarak şimdi atanır
    if not hasattr(history, "answered_at") or history.answered_at is None:
        history.answered_at = datetime.utcnow()
    return service.create(db, history)


# GET ALL
@router.get("/")
def get_all_history(db: Session = Depends(get_db)):
    return service.get_all(db)


# GET BY USER
@router.get("/user/{user_id}")
def get_history_by_user(user_id: int, db: Session = Depends(get_db)):
    records = service.get_by_user(db, user_id)
    if not records:
        raise HTTPException(status_code=404, detail="No history found for this user")
    return records
