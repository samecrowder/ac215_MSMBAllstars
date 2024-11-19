import os
from dotenv import load_dotenv
import fastapi
from model.router import router as model_router
from chat.router import router as chat_router
from external.model_service import initialize_data

if os.environ.get("ENV") != "prod":
    load_dotenv("../.env.dev")


def create_app():
    app = fastapi.FastAPI()

    app.include_router(model_router)
    app.include_router(chat_router)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app


if os.environ.get("ENV") != "test":
    initialize_data()

app = create_app()
