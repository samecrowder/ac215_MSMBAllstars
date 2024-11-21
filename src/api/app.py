import os
from dotenv import load_dotenv
import fastapi
from model.router import router as model_router
from chat.router import router as chat_router
from external.db_service import initialize_data
from cors import setup_cors
import time
from fastapi import Request
import logging

if os.environ.get("ENV") != "prod":
    load_dotenv("../.env.dev")

# This is slightly hacky, but it was the best way I could find to make sure we don't try to make a
# call to GCS during unit/integration tests
if os.environ.get("ENV") != "test":
    initialize_data()

async def log_timing_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    end_time = time.time()
    duration = (end_time - start_time) * 1000  # Convert to milliseconds
    logging.info(f"{request.method} {request.url.path} took {duration:.3f} ms")
    return response

def create_app():
    app = fastapi.FastAPI()
    setup_cors(app)
    
    # Add timing middleware
    app.middleware("http")(log_timing_middleware)

    app.include_router(model_router)
    app.include_router(chat_router)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app


app = create_app()
