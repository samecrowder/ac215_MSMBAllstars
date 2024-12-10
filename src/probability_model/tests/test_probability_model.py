import os
from model import scale_data
import pytest
import numpy as np
from sklearn.preprocessing import StandardScaler


# Create a more sophisticated mock for torch
class TorchMock:
    def __init__(self):
        self.nn = nn
        self.device = lambda x: x

    def ones(self, size):
        return np.ones(size)

    def tensor(self, data):
        return np.array(data)

    def from_numpy(self, data):
        return data

    def cat(self, tensors, dim=0):
        return np.concatenate(tensors, axis=dim)

    def bmm(self, x, y):
        return np.einsum("bij,bjk->bik", x, y)

    def softmax(self, x, dim=-1):
        return np.exp(x) / np.sum(np.exp(x), axis=dim, keepdims=True)

    def sum(self, x, dim=None, keepdim=False):
        return np.sum(x, axis=dim, keepdims=keepdim)

    def mean(self, x, dim=None, keepdim=False):
        return np.mean(x, axis=dim, keepdims=keepdim)

    def sigmoid(self, x):
        return 1 / (1 + np.exp(-x))


class ModuleMock:
    def __init__(self):
        pass

    def to(self, device):
        return self

    def eval(self):
        return self


class DropoutMock:
    def __init__(self, p=0.5, inplace=False):
        self.p = p
        self.inplace = inplace

    def __call__(self, x):
        return x


class TanhMock:
    def __call__(self, x):
        return np.tanh(x)


class ReLUMock:
    def __init__(self):
        pass

    def __call__(self, x):
        return np.maximum(0, x)


class LSTMMock:
    def __init__(
        self, input_size, hidden_size, num_layers, batch_first=False, dropout=0
    ):
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.batch_first = batch_first
        self.dropout = dropout

    def __call__(self, x, *args, **kwargs):
        return x, (None, None)


class LinearMock:
    def __init__(self, in_features, out_features):
        self.in_features = in_features
        self.out_features = out_features

    def __call__(self, x):
        return x


class BatchNorm1dMock:
    def __init__(self, num_features):
        self.num_features = num_features

    def __call__(self, x):
        return x


class LayerNormMock:
    def __init__(self, normalized_shape):
        self.normalized_shape = normalized_shape

    def __call__(self, x):
        return x


class SequentialMock:
    def __init__(self, *args):
        self.layers = args

    def __call__(self, x):
        for layer in self.layers:
            x = layer(x)
        return x


class ParameterMock:
    def __init__(self, data):
        self.data = data


# Set up nn module
class nn:
    Module = ModuleMock
    LSTM = LSTMMock
    Linear = LinearMock
    BatchNorm1d = BatchNorm1dMock
    LayerNorm = LayerNormMock
    Sequential = SequentialMock
    Parameter = ParameterMock
    Dropout = DropoutMock
    Tanh = TanhMock
    ReLU = ReLUMock


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
    X1_scaled, X2_scaled = scale_data(X1, X2, scaler_X1, scaler_X2)

    assert X1_scaled.shape == X1.shape
    assert X2_scaled.shape == X2.shape


def test_tennis_lstm_init():
    """Test TennisLSTM initialization"""
    os.environ["ENV"] = "test"

    # Set up mocks
    import model

    model.nn = nn
    model.torch = TorchMock()

    # Create model
    tennis_lstm = model.TennisLSTM(input_size=10, hidden_size=20, num_layers=2)

    # Test initialization
    assert tennis_lstm.lstm.input_size == 10
    assert tennis_lstm.lstm.hidden_size == 20
    assert tennis_lstm.lstm.num_layers == 2
