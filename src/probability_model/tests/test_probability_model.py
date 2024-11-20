import sys
import os
import pytest
import torch
import numpy as np
from sklearn.preprocessing import StandardScaler

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model import TennisLSTM, scale_data


@pytest.fixture
def sample_data():
    # Create sample data
    samples = 10
    time_steps = 5
    features = 3
    h2h_size = 2

    X1 = np.random.randn(samples, time_steps, features)
    X2 = np.random.randn(samples, time_steps, features)
    H2H = np.random.randn(samples, h2h_size)

    return X1, X2, H2H, features, h2h_size


@pytest.fixture
def scalers():
    return StandardScaler(), StandardScaler(), StandardScaler()


def test_scale_data(sample_data, scalers):
    X1, X2, H2H, _, _ = sample_data
    scaler_X1, scaler_X2, scaler_H2H = scalers

    # Fit scalers
    samples, time_steps, features = X1.shape
    scaler_X1.fit(X1.reshape(-1, features))
    scaler_X2.fit(X2.reshape(-1, features))

    # Test scaling
    X1_scaled, X2_scaled, H2H_scaled = scale_data(
        X1, X2, H2H, scaler_X1, scaler_X2, scaler_H2H
    )

    assert X1_scaled.shape == X1.shape
    assert X2_scaled.shape == X2.shape
    assert H2H_scaled.shape == H2H.shape


def test_tennis_lstm_forward(sample_data):
    X1, X2, H2H, features, h2h_size = sample_data

    # Convert to torch tensors
    X1 = torch.FloatTensor(X1)
    X2 = torch.FloatTensor(X2)
    H2H = torch.FloatTensor(H2H)

    # Initialize model
    hidden_size = 32
    num_layers = 2
    model = TennisLSTM(features, hidden_size, num_layers, h2h_size)

    # Test forward pass
    output = model(X1, X2, H2H)

    assert output.shape == (X1.shape[0], 1)
    assert torch.all((output >= 0) & (output <= 1))


def test_tennis_lstm_architecture(sample_data):
    _, _, _, features, h2h_size = sample_data
    hidden_size = 32
    num_layers = 2

    model = TennisLSTM(features, hidden_size, num_layers, h2h_size)

    # Test model components
    assert isinstance(model.lstm, torch.nn.LSTM)
    assert isinstance(model.fc, torch.nn.Linear)
    assert isinstance(model.fc2, torch.nn.Linear)
    assert isinstance(model.dropout, torch.nn.Dropout)
    assert isinstance(model.relu, torch.nn.ReLU)

    # Test LSTM parameters
    assert model.lstm.input_size == features
    assert model.lstm.hidden_size == hidden_size
    assert model.lstm.num_layers == num_layers

    # Test Linear layer dimensions
    assert model.fc.in_features == hidden_size * 2 + h2h_size
    assert model.fc.out_features == 64
    assert model.fc2.in_features == 64
    assert model.fc2.out_features == 1
