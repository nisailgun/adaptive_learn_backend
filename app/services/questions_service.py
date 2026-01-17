from app.models.user import DifficultyLevel, Question
from app.schemas.user import QuestionCreate, QuestionUpdate
from sqlalchemy.orm import Session

class QuestionService:
    def create(self, db: Session, question: QuestionCreate):
        db_question = Question(
            lesson_id=question.lesson_id,
            text=question.text,
            correct_answer=question.correct_answer,
            difficulty=question.difficulty
        )
        db.add(db_question)
        db.commit()
        db.refresh(db_question)
        return db_question

    def get_all(self, db: Session):
        return db.query(Question).all()

    def get(self, db: Session, question_id: int):
        return db.query(Question).filter(Question.id == question_id).first()

    def update(self, db: Session, question_id: int, question: QuestionUpdate):
        db_question = db.query(Question).filter(Question.id == question_id).first()
        if not db_question:
            return None
        for field, value in question.dict(exclude_unset=True).items():
            setattr(db_question, field, value)
        db.commit()
        db.refresh(db_question)
        return db_question

    def delete(self, db: Session, question_id: int):
        db_question = db.query(Question).filter(Question.id == question_id).first()
        if not db_question:
            return None
        db.delete(db_question)
        db.commit()
        return db_question
    
    @staticmethod
    def get_prioritized_question(db: Session, lesson_id: int):
        priorities = [
            DifficultyLevel.easy,
            DifficultyLevel.medium,
            DifficultyLevel.hard
        ]

        for level in priorities:
            question = (
                db.query(Question)
                .filter(
                    Question.lesson_id == lesson_id,
                    Question.difficulty == level
                )
                .first()
            )
            if question:
                return question

        return None
