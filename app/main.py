from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel
import openai
import os
from app.core.database import engine, Base
from app.api.routes import  auth, history, lessons, protected, questions
from app.core.config import settings
openai.api_key = settings.openai_api_key
# .env dosyasını yükle

# OpenAI API key'i .env'den al

app = FastAPI(title="Simple ChatGPT Endpoint")

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": request.message}],
            max_tokens=200
        )
        reply = response.choices[0].message.content
        return ChatResponse(reply=reply)
    except Exception as e:
        return ChatResponse(reply=f"Error: {str(e)}")
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
app.include_router(history.router)
app.include_router(lessons.router)
app.include_router(questions.router)


# ✅ DUMMY ENDPOINT (PUBLIC)
@app.get("/dummy")
def dummy():
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": "Merhaba"}]
        )
        reply = response.choices[0].message.content
        return ChatResponse(reply=reply)
    except Exception as e:
        return ChatResponse(reply=f"Error: {str(e)}")
