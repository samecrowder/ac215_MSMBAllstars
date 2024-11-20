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
        # we want our requests to be symmetric, so we swap the ids if player_a_id > player_b_id
        # this guarantees that the probability we return is consistent regardless of the order of the ids
        should_swap = request.player_a_id > request.player_b_id
        first_id = request.player_a_id if not should_swap else request.player_b_id
        second_id = request.player_b_id if not should_swap else request.player_a_id
        probability = get_victory_prediction(
            first_id, second_id, request.lookback
        )
        logger.info(f"Received probability from model: {probability}")

        response = PredictionResponse(
            player_a_win_probability=probability if not should_swap else 1 - probability
        )
        logger.info(f"Returning prediction response: {response}")
        return response

    except Exception as e:
        logger.error(f"Error during prediction: {str(e)}")
        logger.exception("Full traceback:")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")
