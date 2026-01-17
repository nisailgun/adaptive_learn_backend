from pydantic import BaseModel, ConfigDict, EmailStr
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
    correct_answer:str
    difficulty: DifficultyLevel

class QuestionCreate(QuestionBase):
    lesson_id: int

class QuestionUpdate(BaseModel):
    text: Optional[str] = None
    correct_answer: Optional[str] = None
    difficulty: Optional[DifficultyLevel] = None
    lesson_id: Optional[int] = None

class Question(QuestionBase):
    id: int
    lesson: Lesson

    class Config:
        orm_mode = True

class HistoryBase(BaseModel):
    student_id: int
    question_id: int
    time_taken_seconds: float
    correct: Optional[float] = None

class HistoryCreate(HistoryBase):
    answered_at: Optional[datetime] = None  # <-- bu satırı ekledik

class HistoryUpdate(BaseModel):
    student_id: Optional[int] = None
    question_id: Optional[int] = None
    time_taken_seconds: Optional[float] = None
    correct: Optional[float] = None
    answered_at: Optional[datetime] = None

class History(HistoryBase):
    id: int
    answered_at: datetime
    question: Question

    class Config:
        from_attributes = True  # eski orm_mode yerine bu
        
class QuestionResponse(BaseModel):
    id: int
    text: str
    difficulty: DifficultyLevel

    model_config = ConfigDict(from_attributes=True)


class AnswerSubmit(BaseModel):
    email: str
    question_id: int
    answer: str
    time_taken_seconds: float


class NextQuestionRequest(BaseModel):
    email: str
    previous_question_id: Optional[int] = None
    previous_correct: Optional[int] = None  # 1 = doğru, 0 = yanlış
    time_taken_seconds: Optional[float] = None


class NextQuestionResponse(BaseModel):
    previous_correct: Optional[int]
    question: Optional[QuestionResponse]
    message: Optional[str]
    

class AnswerAndNextRequest(BaseModel):
    email: str
    question_id: int
    answer: str
    time_taken_seconds: float


class AnswerAndNextResponse(BaseModel):
    correct: int
    next_question: QuestionResponse | None
    message: str | None

class LessonAIPromptResponse(BaseModel):
    lesson_id: int
    lesson_title: str
    lesson_difficulty: str
    prompt: str
    
class LessonAIResponse(BaseModel):
    lesson_id: int
    lesson_title: str
    lesson_difficulty: str
    ai_response: str