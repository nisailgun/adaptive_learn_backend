from fastapi import APIRouter, Depends, HTTPException
from app.core.dependencies import get_current_user
from sqlalchemy.orm import Session
from app.schemas.user import LessonAIPromptResponse, LessonAIResponse, LessonCreate, LessonUpdate
from app.models.user import History, Lesson, Question
from app.services.lessons_service import LessonService
from app.core.database import SessionLocal
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()


import os

client = OpenAI(api_key=os.getenv("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"))


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

@router.post("/{lesson_id}/ai-generate", response_model=LessonAIResponse)
def generate_ai_content(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # 1️⃣ Lesson
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    # 2️⃣ Max 5 soru
    questions = (
        db.query(Question)
        .filter(Question.lesson_id == lesson.id)
        .limit(5)
        .all()
    )

    question_ids = [q.id for q in questions]

    # 3️⃣ Max 2 history
    histories = []
    if question_ids:
        histories = (
            db.query(History)
            .filter(History.question_id.in_(question_ids))
            .order_by(History.answered_at.desc())
            .limit(2)
            .all()
        )

    # 4️⃣ PROMPT
    prompt = f"""
Sen deneyimli bir eğitim asistanısın.

Ders Bilgisi:
- Ders adı: {lesson.title}
- Zorluk seviyesi: {lesson.difficulty}

"""

    if questions:
        prompt += "Bu derste sorulan sorular:\n"
        for i, q in enumerate(questions, start=1):
            prompt += f"{i}. ({q.difficulty}) {q.text}\n"
    else:
        prompt += "Bu derste henüz soru sorulmamıştır.\n"

    if histories:
        prompt += "\nÖğrencilerin verdiği bazı cevaplar:\n"
        for h in histories:
            result = "doğru" if h.correct else "yanlış"
            prompt += (
                f"- Soru ID {h.question_id}: {result}, "
                f"süre: {h.time_taken_seconds} saniye\n"
            )
    else:
        prompt += "\nHenüz öğrenci cevabı bulunmamaktadır.\n"

    prompt += """
Görevlerin:
1. Öğrencinin seviyesini analiz et
2. Zorlandığı noktaları belirle
3. Bu ders için 3 yeni soru üret
4. Her soru için kısa bir açıklama ekle
"""

    # 5️⃣ OPENAI CALL
    try:
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Sen bir eğitim uzmanısın."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    ai_text = completion.choices[0].message.content

    return LessonAIResponse(
        lesson_id=lesson.id,
        lesson_title=lesson.title,
        lesson_difficulty=lesson.difficulty,
        ai_response=ai_text
    )