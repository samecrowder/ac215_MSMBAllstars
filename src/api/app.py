import os

if os.environ.get("ENV") != "prod":
    from dotenv import load_dotenv

    load_dotenv("../.env.dev")

import fastapi

from .model.router import router as model_router
from .chat.router import router as chat_router

app = fastapi.FastAPI()

app.include_router(model_router, prefix="/model")
app.include_router(chat_router, prefix="/chat")


@app.get("/health")
def health():
    return {"status": "ok"}
