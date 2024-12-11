import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200


def test_predict_endpoint_valid_input():
    test_data = {
        "X1": [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]],
        "X2": [[0.7, 0.8, 0.9], [1.0, 1.1, 1.2]],
        "M1": [1, 1],
        "M2": [1, 1],
    }
    response = client.post("/predict", json=test_data)
    assert response.status_code == 200
    assert "player_a_win_probability" in response.json()
    assert 0 <= response.json()["player_a_win_probability"] <= 1


@pytest.mark.parametrize(
    "invalid_data",
    [
        {
            # missing X1, M2
            "X2": [[0.7, 0.8, 0.9]],
            "M1": [1],
        },
        {
            # missing feature in X1
            "X1": [[0.7, 0.8, 0.9]],
            "X2": [[0.7, 0.8, 0.9], [1.0, 1.1, 1.2]],
            "M1": [1, 0],
            "M2": [1, 0],
        },
        {
            # extra feature in X1
            "X1": [[0.7, 0.8, 0.9], [1.0, 1.1, 1.2]],
            "X2": [[0.7, 0.8, 0.9]],
            "M1": [1],
            "M2": [1],
        },
        {"X1": [], "X2": [], "M1": [], "M2": []},  # Empty arrays
        {"X1": None, "X2": None, "M1": None, "M2": None},  # None values
    ],
)
def test_predict_endpoint_edge_cases(invalid_data):
    response = client.post("/predict", json=invalid_data)
    assert response.status_code in [400, 422]
