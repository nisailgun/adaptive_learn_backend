from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.user import LessonCreate, LessonUpdate
from app.models.user import Lesson
from app.services.lessons_service import LessonService
from app.core.database import SessionLocal

router = APIRouter(prefix="/lessons", tags=["Lessons"])
service = LessonService()

# DB bağlantısı
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# CREATE
@router.post("/")
def create_lesson(lesson: LessonCreate, db: Session = Depends(get_db)):
    return service.create(db, lesson)


# GET ALL
@router.get("/")
def get_lessons(db: Session = Depends(get_db)):
    return service.get_all(db)


# GET BY ID
@router.get("/{lesson_id}")
def get_lesson(lesson_id: int, db: Session = Depends(get_db)):
    lesson = service.get(db, lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return lesson


# UPDATE
@router.put("/{lesson_id}")
def update_lesson(lesson_id: int, lesson: LessonUpdate, db: Session = Depends(get_db)):
    updated = service.update(db, lesson_id, lesson)
    if not updated:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return updated


# DELETE
@router.delete("/{lesson_id}")
def delete_lesson(lesson_id: int, db: Session = Depends(get_db)):
    deleted = service.delete(db, lesson_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return {"detail": "Lesson deleted"}
