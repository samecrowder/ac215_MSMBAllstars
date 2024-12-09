import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get environment
ENV = os.getenv("ENV", "dev")
logger.info(f"Current environment: ENV={ENV}")

# Local Docker Compose environment
MODEL_HOST = os.getenv("MODEL_HOST", "probability_model")
MODEL_PORT = os.getenv("MODEL_PORT", "8001")
LLM_HOST = os.getenv("LLM_HOST", "llm")
LLM_PORT = os.getenv("LLM_PORT", "8002")
MODEL_BASE_URL = f"http://{MODEL_HOST}:{MODEL_PORT}"
LLM_BASE_URL = f"http://{LLM_HOST}:{LLM_PORT}"
