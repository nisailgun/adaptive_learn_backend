from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.user import Question
from app.schemas.user import QuestionCreate, QuestionUpdate
from app.services.questions_service import QuestionService
from app.core.database import SessionLocal

router = APIRouter(prefix="/questions", tags=["Questions"])
service = QuestionService()

# DB bağlantısı
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# CREATE
@router.post("/")
def create_question(question: QuestionCreate, db: Session = Depends(get_db)):
    return service.create(db, question)


# GET ALL
@router.get("/")
def get_questions(db: Session = Depends(get_db)):
    return service.get_all(db)


# GET BY ID
@router.get("/{question_id}")
def get_question(question_id: int, db: Session = Depends(get_db)):
    question = service.get(db, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return question


# UPDATE
@router.put("/{question_id}")
def update_question(question_id: int, question: QuestionUpdate, db: Session = Depends(get_db)):
    updated = service.update(db, question_id, question)
    if not updated:
        raise HTTPException(status_code=404, detail="Question not found")
    return updated


# DELETE
@router.delete("/{question_id}")
def delete_question(question_id: int, db: Session = Depends(get_db)):
    deleted = service.delete(db, question_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Question not found")
    return {"detail": "Question deleted"}
