import os

# Get environment
ENV = os.getenv("ENV", "dev")

# Service URLs configuration
if ENV == "dev":
    # Local Docker Compose environment
    MODEL_HOST = os.getenv("MODEL_HOST", "probability_model")
    MODEL_PORT = os.getenv("MODEL_PORT", "8001")
    LLM_HOST = os.getenv("LLM_HOST", "llm")
    LLM_PORT = os.getenv("LLM_PORT", "8002")

    MODEL_BASE_URL = f"http://{MODEL_HOST}:{MODEL_PORT}"
    LLM_BASE_URL = f"http://{LLM_HOST}:{LLM_PORT}"
else:
    # Cloud Run environment - full URLs including protocol
    MODEL_BASE_URL = os.getenv("MODEL_BASE_URL", "http://probability-model:8001")
    LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://llm:8002")
