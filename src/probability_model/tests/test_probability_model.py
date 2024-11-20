import os
import pickle
from io import BytesIO
import sys
import pytest
import torch
import numpy as np
from fastapi.testclient import TestClient
from sklearn.preprocessing import StandardScaler

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model import TennisLSTM, scale_data
from app import app, read_pt_file_from_gcs, read_pkl_file_from_gcs


@pytest.fixture
def sample_data():
    # Create sample data
    samples = 10
    time_steps = 5
    features = 3
    h2h_size = 2
    
    X1 = np.random.rand(samples, time_steps, features)
    X2 = np.random.rand(samples, time_steps, features) 
    H2H = np.random.rand(samples, h2h_size)
    
    return X1, X2, H2H, features, h2h_size

def test_tennis_lstm_forward(sample_data):
    X1, X2, H2H, features, h2h_size = sample_data
    
    # Initialize model
    hidden_size = 32
    num_layers = 2
    model = TennisLSTM(features, hidden_size, num_layers, h2h_size)
    
    # Convert inputs to tensors
    X1_tensor = torch.FloatTensor(X1)
    X2_tensor = torch.FloatTensor(X2)
    H2H_tensor = torch.FloatTensor(H2H)
    
    # Test forward pass
    output = model(X1_tensor, X2_tensor, H2H_tensor)
    
    # Check output shape and values
    assert output.shape == (X1.shape[0], 1)
    assert torch.all((output >= 0) & (output <= 1))

def test_scale_data(sample_data):
    X1, X2, H2H, _, _ = sample_data
    
    # Initialize scalers
    scaler_X1 = StandardScaler()
    scaler_X2 = StandardScaler()
    scaler_H2H = StandardScaler()
    
    # Fit scalers on reshaped data
    scaler_X1.fit(X1.reshape(-1, X1.shape[-1]))
    scaler_X2.fit(X2.reshape(-1, X2.shape[-1]))
    
    # Scale data
    X1_scaled, X2_scaled, H2H_scaled = scale_data(X1, X2, H2H, scaler_X1, scaler_X2, scaler_H2H)
    
    # Check shapes are preserved
    assert X1_scaled.shape == X1.shape
    assert X2_scaled.shape == X2.shape
    assert H2H_scaled.shape == H2H.shape
    
    # Check scaling was applied (mean close to 0, std close to 1)
    assert np.abs(X1_scaled.reshape(-1, X1.shape[-1]).mean()) < 0.1
    assert np.abs(X2_scaled.reshape(-1, X2.shape[-1]).mean()) < 0.1
    assert np.abs(X1_scaled.reshape(-1, X1.shape[-1]).std() - 1) < 0.1
    assert np.abs(X2_scaled.reshape(-1, X2.shape[-1]).std() - 1) < 0.1

@pytest.fixture
def client():
    return TestClient(app)

def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_predict_endpoint(client, sample_data):
    X1, X2, H2H, _, _ = sample_data
    
    # Prepare request data
    request_data = {
        "X1": X1[0].tolist(),  # Take first sample
        "X2": X2[0].tolist(),
        "H2H": H2H[0].tolist()
    }
    
    response = client.post("/predict", json=request_data)
    
    assert response.status_code == 200
    assert "player_a_win_probability" in response.json()
    prob = response.json()["player_a_win_probability"]
    assert isinstance(prob, float)
    assert 0 <= prob <= 1

def test_predict_endpoint_invalid_data(client):
    # Test with invalid data structure
    invalid_data = {
        "X1": [[1, 2, 3]],
        "X2": "invalid",  # Should be list of lists
        "H2H": [1, 2]
    }
    
    response = client.post("/predict", json=invalid_data)
    assert response.status_code == 422  # Validation error

@pytest.fixture
def mock_gcs_bucket(mocker):
    mock_blob = mocker.Mock()
    mock_blob.download_as_bytes.return_value = b"mock_content"
    
    mock_bucket = mocker.Mock()
    mock_bucket.blob.return_value = mock_blob
    
    return mock_bucket

def test_read_pt_file_from_gcs(mock_gcs_bucket, mocker):
    mock_torch_load = mocker.patch('torch.load')
    mock_torch_load.return_value = "mock_tensor"
    
    result = read_pt_file_from_gcs(mock_gcs_bucket, "test.pt")
    
    assert result == "mock_tensor"
    mock_bucket.blob.assert_called_once_with("test.pt")

def test_read_pkl_file_from_gcs(mock_gcs_bucket, mocker):
    mock_pickle_loads = mocker.patch('pickle.loads')
    mock_pickle_loads.return_value = {"mock": "data"}
    
    result = read_pkl_file_from_gcs(mock_gcs_bucket, "test.pkl")
    
    assert result == {"mock": "data"}
    mock_bucket.blob.assert_called_once_with("test.pkl")
