# model routes

from fastapi import APIRouter

from api.external.model_service import get_victory_prediction

router = APIRouter()


@router.get("/predict")
def predict(player_a_id: str, player_b_id: str):
    return {
        "player_a_win_probability": get_victory_prediction(player_a_id, player_b_id)
    }
