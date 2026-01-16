from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import hash_password, verify_password, create_access_token

class AuthService:
    def register(self, db: Session, user):
        hashed = hash_password(user.password)
        db_user = User(email=user.email, hashed_password=hashed, role=user.role)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return {"email": db_user.email, "role": db_user.role}

    def login(self, db: Session, email: str, password: str):
        user = db.query(User).filter(User.email==email).first()
        if not user or not verify_password(password, user.hashed_password):
            return None
        token = create_access_token({"sub": user.email, "role": user.role})
        return token
