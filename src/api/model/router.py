# model routes

from fastapi import APIRouter

from ..external.model_service import get_victory_prediction

router = APIRouter()


@router.post("/predict")
def predict(player_a_id: str, player_b_id: str, lookback: int = 10):
    return {
        "player_a_win_probability": get_victory_prediction(player_a_id, player_b_id, lookback)
    }
