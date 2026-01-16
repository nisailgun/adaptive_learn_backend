from fastapi import APIRouter, Depends, HTTPException
from app.core.security import hash_password
from app.models.user import User
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.schemas.user import UserCreate, UserLogin, TokenResponse
from app.services.auth_service import AuthService
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])
auth_service = AuthService()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    try:
        hashed = hash_password(user.password)
        db_user = User(email=user.email, hashed_password=hashed)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return {"message": "User created", "user_id": db_user.id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login", response_model=TokenResponse)
def login(data: UserLogin, db: Session = Depends(get_db)):
    token = auth_service.login(db, data.email, data.password)
    if not token:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"access_token": token}
