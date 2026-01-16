from app.models.user import Lesson
from app.schemas.user import LessonCreate, LessonUpdate
from sqlalchemy.orm import Session


class LessonService:
    def create(self, db: Session, lesson: LessonCreate):
        db_lesson = Lesson(title=lesson.title, difficulty=lesson.difficulty)
        db.add(db_lesson)
        db.commit()
        db.refresh(db_lesson)
        return db_lesson

    def get_all(self, db: Session):
        return db.query(Lesson).all()

    def get(self, db: Session, lesson_id: int):
        return db.query(Lesson).filter(Lesson.id == lesson_id).first()

    def update(self, db: Session, lesson_id: int, lesson: LessonUpdate):
        db_lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
        if not db_lesson:
            return None
        for field, value in lesson.dict(exclude_unset=True).items():
            setattr(db_lesson, field, value)
        db.commit()
        db.refresh(db_lesson)
        return db_lesson

    def delete(self, db: Session, lesson_id: int):
        db_lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
        if not db_lesson:
            return None
        db.delete(db_lesson)
        db.commit()
        return db_lesson
