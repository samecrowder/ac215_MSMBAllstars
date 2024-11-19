# model routes
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from external.model_service import get_victory_prediction

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()


class PredictionRequest(BaseModel):
    player_a_id: str
    player_b_id: str
    lookback: int = 10  # Default value if not provided


class PredictionResponse(BaseModel):
    player_a_win_probability: float


@router.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest):
    try:
        probability = get_victory_prediction(
            request.player_a_id, request.player_b_id, request.lookback
        )
        logger.info(f"Received probability from model: {probability}")

        response = PredictionResponse(player_a_win_probability=probability)
        logger.info(f"Returning prediction response: {response}")
        return response

    except Exception as e:
        logger.error(f"Error during prediction: {str(e)}")
        logger.exception("Full traceback:")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")
