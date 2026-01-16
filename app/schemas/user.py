from pydantic import BaseModel, EmailStr
from enum import Enum
from typing import List, Optional
from datetime import datetime

# Kullanıcı rolleri
class UserRole(str, Enum):
    student = "student"
    teacher = "teacher"
    admin = "admin"

# Zorluk seviyeleri
class DifficultyLevel(str, Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"

# Kullanıcı şemaları
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: UserRole

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

# Ders şemaları
class LessonBase(BaseModel):
    title: str
    difficulty: DifficultyLevel

class LessonCreate(LessonBase):
    pass

class LessonUpdate(BaseModel):
    title: Optional[str] = None
    difficulty: Optional[DifficultyLevel] = None

class Lesson(LessonBase):
    id: int
    questions: List["Question"] = []

    class Config:
        orm_mode = True

# Soru şemaları
class QuestionBase(BaseModel):
    text: str
    difficulty: DifficultyLevel

class QuestionCreate(QuestionBase):
    lesson_id: int

class QuestionUpdate(BaseModel):
    text: Optional[str] = None
    difficulty: Optional[DifficultyLevel] = None
    lesson_id: Optional[int] = None

class Question(QuestionBase):
    id: int
    lesson: Lesson

    class Config:
        orm_mode = True

# History şemaları
class HistoryBase(BaseModel):
    student_id: int
    question_id: int
    time_taken_seconds: float

class HistoryCreate(HistoryBase):
    pass

class HistoryUpdate(BaseModel):
    time_taken_seconds: Optional[float] = None
    question_id: Optional[int] = None
    student_id: Optional[int] = None

class History(HistoryBase):
    id: int
    answered_at: datetime
    question: Question

    class Config:
        orm_mode = True
