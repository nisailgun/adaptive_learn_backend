from fastapi import APIRouter, Depends
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/protected", tags=["Protected"])

@router.get("/me")
def me(current_user: dict = Depends(get_current_user)):
    return {"email": current_user["sub"], "role": current_user["role"]}

@router.get("/dummy")
def dummy(current_user: dict = Depends(get_current_user)):
    return {"message": "Hello, this is a dummy endpoint!", "user": current_user}
