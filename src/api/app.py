import os
from dotenv import load_dotenv
import fastapi
from model.router import router as model_router
from chat.router import router as chat_router
from external.model_service import initialize_data
from cors import setup_cors

if os.environ.get("ENV") != "prod":
    load_dotenv("../.env.dev")

# This is slightly hacky, but it was the best way I could find to make sure we don't try to make a
# call to GCS during unit/integration tests
if os.environ.get("ENV") != "test":
    initialize_data()


def create_app():
    app = fastapi.FastAPI()
    setup_cors(app)

    app.include_router(model_router)
    app.include_router(chat_router)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app


app = create_app()
