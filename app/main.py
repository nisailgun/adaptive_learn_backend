from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import engine, Base
from app.api.routes import auth, protected

# 🔥 TABLOLAR OTOMATİK OLUŞUR
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Adaptive Learning Backend")

# 🌍 CORS – HER ŞEYE AÇIK
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔗 ROUTER'LAR
app.include_router(auth.router)
app.include_router(protected.router)

# ✅ DUMMY ENDPOINT (PUBLIC)
@app.get("/dummy")
def dummy():
    return {
        "status": "ok",
        "message": "Dummy endpoint çalışıyor 🚀"
    }
