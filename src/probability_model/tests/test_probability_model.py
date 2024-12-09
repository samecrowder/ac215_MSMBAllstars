import sys
import os
from unittest.mock import MagicMock
from model import scale_data
import pytest
import numpy as np
from sklearn.preprocessing import StandardScaler

# Create a more sophisticated mock for torch
mock_torch = MagicMock()


# Create a tensor mock that preserves shape
class TensorMock:
    def __init__(self, shape):
        self.shape = shape

    def to(self, *args, **kwargs):
        return self


mock_torch.tensor = lambda x: TensorMock(x.shape)
mock_torch.device = lambda x: x


# Create module mocks that return proper shapes
class LSTMMock(MagicMock):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.input_size = kwargs.get("input_size")
        self.hidden_size = kwargs.get("hidden_size")
        self.num_layers = kwargs.get("num_layers")

    def __call__(self, x, *args, **kwargs):
        batch_size = x.shape[0]
        return TensorMock((batch_size, x.shape[1], self.hidden_size)), None


class LinearMock(MagicMock):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.in_features = args[0]
        self.out_features = args[1]

    def __call__(self, x, *args, **kwargs):
        return TensorMock((x.shape[0], self.out_features))


# Set up nn mocks
mock_torch.nn = MagicMock()
mock_torch.nn.LSTM = LSTMMock
mock_torch.nn.Linear = LinearMock
mock_torch.nn.Dropout = MagicMock
mock_torch.nn.ReLU = MagicMock
mock_torch.nn.Module = MagicMock
mock_torch.nn.Sigmoid = MagicMock

sys.modules["torch"] = mock_torch
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


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
