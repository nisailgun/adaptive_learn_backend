from sqlalchemy import Column, Integer, String, Enum, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum
from datetime import datetime

# Kullanıcı rolleri
class UserRole(str, enum.Enum):
    student = "student"
    teacher = "teacher"
    admin = "admin"

# Zorluk seviyeleri
class DifficultyLevel(str, enum.Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"

# Kullanıcı
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False)

    # Öğrencinin cevap geçmişi
    histories = relationship("History", back_populates="student")

# Ders
class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    difficulty = Column(Enum(DifficultyLevel), nullable=False)

    # Dersin soruları
    questions = relationship("Question", back_populates="lesson")

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False)
    text = Column(String(1024), nullable=False)
    difficulty = Column(Enum(DifficultyLevel), nullable=False)
    correct_answer = Column(String(255), nullable=True)
    lesson = relationship("Lesson", back_populates="questions")
    histories = relationship("History", back_populates="question")

# Öğrenci cevap geçmişi
class History(Base):
    __tablename__ = "histories"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    time_taken_seconds = Column(Float, nullable=False)
    answered_at = Column(DateTime, default=datetime.utcnow)
    correct=Column(Float, nullable=True)

    student = relationship("User", back_populates="histories")
    question = relationship("Question", back_populates="histories")
