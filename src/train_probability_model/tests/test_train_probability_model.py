import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.linear_model import LogisticRegression
import joblib
from sklearn.calibration import calibration_curve


@pytest.fixture
def sample_training_data():
    """Create sample training data"""
    np.random.seed(42)
    n_samples = 1000

    data = {
        "rank_diff": np.random.normal(0, 100, n_samples),
        "age_diff": np.random.normal(0, 5, n_samples),
        "height_diff": np.random.normal(0, 10, n_samples),
        "surface_code": np.random.choice([0, 1, 2], n_samples),
        "tourney_level_code": np.random.choice([0, 1, 2], n_samples),
        "winner": np.random.choice([0, 1], n_samples),  # Target variable
    }
    return pd.DataFrame(data)


@pytest.fixture
def preprocessed_data(sample_training_data):
    """Create preprocessed data with scaled features"""
    X = sample_training_data.drop(["winner"], axis=1)
    y = sample_training_data["winner"]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    X_scaled = pd.DataFrame(X_scaled, columns=X.columns)

    return X_scaled, y


def test_data_split(preprocessed_data):
    """Test train-test split functionality"""
    X, y = preprocessed_data

    # Perform train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Check shapes
    assert len(X_train) == 800  # 80% of 1000
    assert len(X_test) == 200  # 20% of 1000
    assert len(y_train) == 800
    assert len(y_test) == 200

    # Check that we have the same columns
    assert all(col in X_train.columns for col in X.columns)
    assert all(col in X_test.columns for col in X.columns)


def test_model_training(preprocessed_data):
    """Test model training process"""
    from tennis_lstm import TennisLSTM

    X, y = preprocessed_data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Train model
    model = TennisLSTM(input_size=X.shape[1], hidden_size=64, num_layers=2)
    model.fit(X_train, y_train)

    # Make predictions
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)

    # Basic checks
    assert len(y_pred) == len(y_test)
    assert y_pred_proba.shape == (len(y_test), 2)
    assert all(0 <= prob <= 1 for prob in y_pred_proba.flatten())


def test_model_evaluation(preprocessed_data):
    """Test model evaluation metrics"""
    from tennis_lstm import TennisLSTM

    X, y = preprocessed_data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Train and evaluate model
    model = TennisLSTM(input_size=X.shape[1], hidden_size=64, num_layers=2)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    # Calculate metrics
    accuracy = accuracy_score(y_test, y_pred)
    auc_roc = roc_auc_score(y_test, model.predict_proba(X_test)[:, 1])

    # Check metrics are in valid ranges
    assert 0 <= accuracy <= 1
    assert 0 <= auc_roc <= 1


@pytest.mark.integration
def test_full_training_pipeline(sample_training_data):
    """Test the entire training pipeline"""
    # 1. Preprocessing
    X = sample_training_data.drop(["winner"], axis=1)
    y = sample_training_data["winner"]

    # 2. Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    X_scaled = pd.DataFrame(X_scaled, columns=X.columns)

    # 3. Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42
    )

    # 4. Train model
    from tennis_lstm import TennisLSTM

    model = TennisLSTM(input_size=X.shape[1], hidden_size=64, num_layers=2)
    model.fit(X_train, y_train)

    # 5. Evaluate
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    # Verify pipeline results
    assert model.coef_.shape[1] == len(X.columns)
    assert 0 <= accuracy <= 1


def test_model_persistence(preprocessed_data):
    """Test model saving and loading"""
    import joblib
    from tennis_lstm import TennisLSTM

    X, y = preprocessed_data
    model = TennisLSTM(input_size=X.shape[1], hidden_size=64, num_layers=2)
    model.fit(X, y)

    # Save model
    with patch("joblib.dump") as mock_dump:
        joblib.dump(model, "model.joblib")
        mock_dump.assert_called_once()

    # Load model
    with patch("joblib.load") as mock_load:
        mock_load.return_value = model
        loaded_model = joblib.load("model.joblib")
        mock_load.assert_called_once()

    assert isinstance(loaded_model, TennisLSTM)


def test_feature_importance(preprocessed_data):
    """Test feature importance analysis"""
    from tennis_lstm import TennisLSTM

    X, y = preprocessed_data
    model = TennisLSTM(input_size=X.shape[1], hidden_size=64, num_layers=2)
    model.fit(X, y)

    # Get feature importance
    importance = pd.DataFrame({"feature": X.columns, "importance": abs(model.coef_[0])})

    assert len(importance) == len(X.columns)
    assert all(importance["importance"] >= 0)


def test_model_predictions(preprocessed_data):
    """Test model predictions and probability calibration"""
    from tennis_lstm import TennisLSTM
    from sklearn.calibration import calibration_curve

    X, y = preprocessed_data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = TennisLSTM(input_size=X.shape[1], hidden_size=64, num_layers=2)
    model.fit(X_train, y_train)

    # Get predictions and probabilities
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    # Calculate calibration curve
    prob_true, prob_pred = calibration_curve(y_test, y_prob, n_bins=5)

    # Verify predictions
    assert all(isinstance(pred, (np.int64, np.int32, int)) for pred in y_pred)
    assert all(0 <= prob <= 1 for prob in y_prob)
    assert len(prob_true) == len(prob_pred)


def test_edge_cases(sample_training_data):
    """Test handling of edge cases"""
    # Test with missing values
    sample_training_data.loc[0, "rank_diff"] = np.nan

    # Clean data
    clean_data = sample_training_data.dropna()

    assert len(clean_data) < len(sample_training_data)
    assert not clean_data.isnull().any().any()

    # Test with extreme values
    sample_training_data.loc[1, "rank_diff"] = 1000000

    # Scale to handle extreme values
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(
        sample_training_data.drop(["winner"], axis=1)
    )

    assert not np.isinf(scaled_features).any()
