from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.user import History, Question, User
from app.schemas.user import AnswerAndNextRequest, AnswerAndNextResponse, AnswerSubmit, NextQuestionRequest, NextQuestionResponse, QuestionCreate, QuestionResponse, QuestionUpdate
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

@router.get("/by-lesson/{lesson_id}", response_model=QuestionResponse)
def get_question_by_lesson_priority(
    lesson_id: int,
    db: Session = Depends(get_db)
):
    for diff in ["easy", "medium", "hard"]:
        q = (
            db.query(Question)
            .filter(
                Question.lesson_id == lesson_id,
                Question.difficulty == diff
            )
            .first()
        )
        if q:
            return q

    raise HTTPException(status_code=404, detail="Bu ders için soru yok")

@router.post("/answer")
def submit_answer(
    payload: AnswerSubmit,
    db: Session = Depends(get_db)
):
    # 1️⃣ Kullanıcıyı email ile bul
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 2️⃣ Soruyu bul
    question = db.query(Question).filter(Question.id == payload.question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    # 3️⃣ Cevap karşılaştır
    is_correct = 1 if payload.answer.strip() == question.correct_answer.strip() else 0

    # 4️⃣ History kaydı oluştur
    history = History(
        student_id=user.id,
        question_id=question.id,
        time_taken_seconds=payload.time_taken_seconds,
        correct=is_correct,
        answered_at=datetime.utcnow()
    )

    db.add(history)
    db.commit()
    db.refresh(history)

    return {
        "detail": "Answer submitted",
        "history_id": history.id,
        "correct": is_correct
    }
@router.post("/next", response_model=NextQuestionResponse)
def get_next_question(
    payload: NextQuestionRequest,
    db: Session = Depends(get_db)
):
    # 1️⃣ User bul
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 2️⃣ Önceki sorudan lesson_id al
    lesson_id = None
    prev_question = None

    if payload.previous_question_id:
        prev_question = (
            db.query(Question)
            .filter(Question.id == payload.previous_question_id)
            .first()
        )
        if not prev_question:
            raise HTTPException(status_code=404, detail="Previous question not found")

        lesson_id = prev_question.lesson_id

    # 3️⃣ Kullanıcının bu derste çözdüğü sorular
    solved_question_ids = (
        db.query(History.question_id)
        .join(Question, Question.id == History.question_id)
        .filter(
            History.student_id == user.id,
            Question.lesson_id == lesson_id
        )
        .subquery()
    )

    # 4️⃣ Hedef difficulty belirleme
    target_difficulty = "easy"

    if payload.time_taken_seconds and payload.time_taken_seconds > 20:
        target_difficulty = "easy"

    elif payload.previous_correct is not None and prev_question:
        if payload.previous_correct == 1:
            target_difficulty = {
                "easy": "medium",
                "medium": "hard",
                "hard": "hard"
            }.get(prev_question.difficulty, "easy")
        else:
            target_difficulty = {
                "hard": "medium",
                "medium": "easy",
                "easy": "easy"
            }.get(prev_question.difficulty, "easy")

    # 5️⃣ Aynı ders + çözülmemiş + difficulty
    question = (
        db.query(Question)
        .filter(
            Question.lesson_id == lesson_id,
            Question.id.notin_(solved_question_ids),
            Question.difficulty == target_difficulty
        )
        .first()
    )
    if not question:
        question = (
            db.query(Question)
            .filter(
                Question.lesson_id == lesson_id,
                Question.id.notin_(solved_question_ids)
            )
            .first()
        )

    if not question:
        return NextQuestionResponse(
            previous_correct=payload.previous_correct,
            question=None,
            message="Bu ders için size uygun çözülmemiş soru yok"
        )

    return NextQuestionResponse(
        previous_correct=payload.previous_correct,
        question=question,
        message=None
    )

@router.post("/answer-and-next", response_model=AnswerAndNextResponse)
def answer_and_get_next_question(
    payload: AnswerAndNextRequest,
    db: Session = Depends(get_db)
):
    # 1️⃣ Kullanıcı
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 2️⃣ Mevcut soru
    question = db.query(Question).filter(Question.id == payload.question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    lesson_id = question.lesson_id

    # 3️⃣ Cevap kontrolü
    is_correct = 1 if payload.answer.strip() == question.correct_answer.strip() else 0

    # 4️⃣ History kaydı
    history = History(
        student_id=user.id,
        question_id=question.id,
        time_taken_seconds=payload.time_taken_seconds,
        correct=is_correct,
        answered_at=datetime.utcnow()
    )
    db.add(history)
    db.commit()

    # 5️⃣ Kullanıcının BU DERSTE çözdüğü sorular
    solved_question_ids = (
        db.query(History.question_id)
        .join(Question, Question.id == History.question_id)
        .filter(
            History.student_id == user.id,
            Question.lesson_id == lesson_id
        )
        .subquery()
    )

    # 6️⃣ Difficulty belirleme
    target_difficulty = "easy"

    if payload.time_taken_seconds > 20:
        target_difficulty = "easy"
    else:
        if is_correct == 1:
            target_difficulty = {
                "easy": "medium",
                "medium": "hard",
                "hard": "hard"
            }.get(question.difficulty, "easy")
        else:
            target_difficulty = {
                "hard": "medium",
                "medium": "easy",
                "easy": "easy"
            }.get(question.difficulty, "easy")

    # 7️⃣ Aynı ders + çözülmemiş + difficulty
    next_question = (
        db.query(Question)
        .filter(
            Question.lesson_id == lesson_id,
            Question.id.notin_(solved_question_ids),
            Question.difficulty == target_difficulty
        )
        .first()
    )

    # 8️⃣ Fallback – aynı ders, başka difficulty
    if not next_question:
        next_question = (
            db.query(Question)
            .filter(
                Question.lesson_id == lesson_id,
                Question.id.notin_(solved_question_ids)
            )
            .first()
        )

    # 9️⃣ Hâlâ soru yoksa
    if not next_question:
        return AnswerAndNextResponse(
            correct=is_correct,
            next_question=None,
            message="Bu ders için çözülmemiş soru kalmadı"
        )

    return AnswerAndNextResponse(
        correct=is_correct,
        next_question=next_question,
        message=None
    )

