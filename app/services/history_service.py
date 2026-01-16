from app.models.user import History
from app.schemas.user import HistoryCreate
from sqlalchemy.orm import Session

class HistoryService:
    def create(self, db: Session, history: HistoryCreate):
        db_history = History(
            user_id=history.user_id,
            question_id=history.question_id,
            seconds_taken=history.seconds_taken,
            answered_at=history.answered_at
        )
        db.add(db_history)
        db.commit()
        db.refresh(db_history)
        return db_history

    def get_all(self, db: Session):
        return db.query(History).all()

    def get_by_user(self, db: Session, user_id: int):
        return db.query(History).filter(History.user_id == user_id).all()
