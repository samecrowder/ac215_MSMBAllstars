# model routes

from fastapi import APIRouter
from pydantic import BaseModel

from ..external.model_service import get_victory_prediction

router = APIRouter()


class PredictionRequest(BaseModel):
    player_a_id: str
    player_b_id: str
    lookback: int = 10  # Default value if not provided


class PredictionResponse(BaseModel):
    player_a_win_probability: float


@router.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest):
    probability = get_victory_prediction(
        request.player_a_id, request.player_b_id, request.lookback
    )
    return PredictionResponse(player_a_win_probability=probability)
