from app.models.user import History, User
from app.schemas.user import HistoryCreate, HistoryUpdate
from sqlalchemy.orm import Session

class HistoryService:
    # -----------------------
    # CREATE
    # -----------------------
    def create(self, db: Session, history: HistoryCreate):
        db_history = History(
            student_id=history.student_id,
            question_id=history.question_id,
            time_taken_seconds=history.time_taken_seconds,
            answered_at=history.answered_at,
            correct=history.correct
        )
        db.add(db_history)
        db.commit()
        db.refresh(db_history)
        return db_history

    # -----------------------
    # READ
    # -----------------------
    def get_all(self, db: Session):
        return db.query(History).all()

    def get_by_student(self, db: Session, student_id: int):
        return db.query(History).filter(History.student_id == student_id).all()

    def get_by_student_email(self, db: Session, email: str):
        return (
            db.query(History)
            .join(User, History.student_id == User.id)
            .filter(User.email == email)
            .all()
        )

    def get(self, db: Session, history_id: int):
        return db.query(History).filter(History.id == history_id).first()

    # -----------------------
    # UPDATE
    # -----------------------
    def update(self, db: Session, history_id: int, history: HistoryUpdate):
        db_history = db.query(History).filter(History.id == history_id).first()
        if not db_history:
            return None
        for field, value in history.dict(exclude_unset=True).items():
            setattr(db_history, field, value)
        db.commit()
        db.refresh(db_history)
        return db_history

    # -----------------------
    # DELETE
    # -----------------------
    def delete(self, db: Session, history_id: int):
        db_history = db.query(History).filter(History.id == history_id).first()
        if not db_history:
            return None
        db.delete(db_history)
        db.commit()
        return db_history
