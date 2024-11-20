import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch
from io import StringIO

@pytest.fixture
def raw_tennis_data():
    """Create a sample raw tennis match data"""
    data = {
        'tourney_date': ['20230101', '20230102', '20230103'],
        'surface': ['Hard', 'Clay', 'Grass'],
        'tourney_level': ['A', 'M', 'G'],
        'winner_name': ['Player A', 'Player B', 'Player C'],
        'loser_name': ['Player D', 'Player E', 'Player F'],
        'winner_rank': [1, 5, 10],
        'loser_rank': [15, 20, 25],
        'winner_rank_points': [8000, 4500, 3000],
        'loser_rank_points': [2000, 1500, 1000],
        'winner_age': [25.5, 28.3, 23.7],
        'loser_age': [22.1, 29.5, 26.8],
        'winner_ht': [185, 190, 188],
        'loser_ht': [182, 178, 185],
        'score': ['6-4 6-3', '7-6(5) 6-4', '6-3 7-5'],
        'minutes': [120, 135, 110]
    }
    return pd.DataFrame(data)

def test_feature_engineering(raw_tennis_data):
    """Test feature engineering process"""
    # Calculate rank difference
    raw_tennis_data['rank_diff'] = raw_tennis_data['winner_rank'] - raw_tennis_data['loser_rank']
    raw_tennis_data['rank_points_diff'] = raw_tennis_data['winner_rank_points'] - raw_tennis_data['loser_rank_points']
    
    # Test new features
    assert 'rank_diff' in raw_tennis_data.columns
    assert 'rank_points_diff' in raw_tennis_data.columns
    assert len(raw_tennis_data['rank_diff']) == 3
    assert not raw_tennis_data['rank_diff'].isnull().any()

def test_surface_encoding(raw_tennis_data):
    """Test surface encoding"""
    # Create surface mapping
    surface_mapping = {'Hard': 0, 'Clay': 1, 'Grass': 2}
    raw_tennis_data['surface_code'] = raw_tennis_data['surface'].map(surface_mapping)
    
    assert 'surface_code' in raw_tennis_data.columns
    assert raw_tennis_data['surface_code'].isin([0, 1, 2]).all()
    assert not raw_tennis_data['surface_code'].isnull().any()

def test_tournament_level_encoding(raw_tennis_data):
    """Test tournament level encoding"""
    # Create tournament level mapping
    level_mapping = {'A': 0, 'M': 1, 'G': 2}
    raw_tennis_data['tourney_level_code'] = raw_tennis_data['tourney_level'].map(level_mapping)
    
    assert 'tourney_level_code' in raw_tennis_data.columns
    assert raw_tennis_data['tourney_level_code'].isin([0, 1, 2]).all()
    assert not raw_tennis_data['tourney_level_code'].isnull().any()

def test_age_features(raw_tennis_data):
    """Test age-related feature engineering"""
    # Calculate age difference and age statistics
    raw_tennis_data['age_diff'] = raw_tennis_data['winner_age'] - raw_tennis_data['loser_age']
    raw_tennis_data['avg_match_age'] = (raw_tennis_data['winner_age'] + raw_tennis_data['loser_age']) / 2
    
    assert 'age_diff' in raw_tennis_data.columns
    assert 'avg_match_age' in raw_tennis_data.columns
    assert not raw_tennis_data['age_diff'].isnull().any()
    assert not raw_tennis_data['avg_match_age'].isnull().any()
    assert (raw_tennis_data['avg_match_age'] >= 0).all()

def test_height_features(raw_tennis_data):
    """Test height-related feature engineering"""
    # Calculate height difference
    raw_tennis_data['height_diff'] = raw_tennis_data['winner_ht'] - raw_tennis_data['loser_ht']
    
    assert 'height_diff' in raw_tennis_data.columns
    assert not raw_tennis_data['height_diff'].isnull().any()
    assert isinstance(raw_tennis_data['height_diff'].iloc[0], (int, float))

def test_score_parsing(raw_tennis_data):
    """Test score parsing functionality"""
    def parse_score(score):
        sets = score.split()
        return len(sets)
    
    raw_tennis_data['num_sets'] = raw_tennis_data['score'].apply(parse_score)
    
    assert 'num_sets' in raw_tennis_data.columns
    assert (raw_tennis_data['num_sets'] >= 2).all()
    assert (raw_tennis_data['num_sets'] <= 5).all()

def test_data_validation(raw_tennis_data):
    """Test data validation checks"""
    # Check for required columns
    required_columns = [
        'tourney_date', 'winner_rank', 'loser_rank',
        'winner_age', 'loser_age', 'winner_ht', 'loser_ht'
    ]
    for col in required_columns:
        assert col in raw_tennis_data.columns
    
    # Check data types
    assert pd.to_numeric(raw_tennis_data['winner_rank'], errors='coerce').notnull().all()
    assert pd.to_numeric(raw_tennis_data['winner_age'], errors='coerce').notnull().all()
    assert pd.to_numeric(raw_tennis_data['winner_ht'], errors='coerce').notnull().all()

def test_date_processing(raw_tennis_data):
    """Test date processing functionality"""
    # Convert tourney_date to datetime
    raw_tennis_data['tourney_date'] = pd.to_datetime(
        raw_tennis_data['tourney_date'],
        format='%Y%m%d'
    )
    
    assert pd.api.types.is_datetime64_any_dtype(raw_tennis_data['tourney_date'])
    assert not raw_tennis_data['tourney_date'].isnull().any()
    assert len(raw_tennis_data['tourney_date'].unique()) == 3

@pytest.mark.integration
def test_full_preprocessing_pipeline(raw_tennis_data):
    """Test the entire preprocessing pipeline"""
    # 1. Date processing
    raw_tennis_data['tourney_date'] = pd.to_datetime(
        raw_tennis_data['tourney_date'],
        format='%Y%m%d'
    )
    
    # 2. Feature engineering
    raw_tennis_data['rank_diff'] = raw_tennis_data['winner_rank'] - raw_tennis_data['loser_rank']
    raw_tennis_data['age_diff'] = raw_tennis_data['winner_age'] - raw_tennis_data['loser_age']
    raw_tennis_data['height_diff'] = raw_tennis_data['winner_ht'] - raw_tennis_data['loser_ht']
    
    # 3. Surface encoding
    surface_mapping = {'Hard': 0, 'Clay': 1, 'Grass': 2}
    raw_tennis_data['surface_code'] = raw_tennis_data['surface'].map(surface_mapping)
    
    # Verify final dataset
    expected_features = [
        'tourney_date', 'rank_diff', 'age_diff',
        'height_diff', 'surface_code'
    ]
    for feature in expected_features:
        assert feature in raw_tennis_data.columns
        assert not raw_tennis_data[feature].isnull().any()

def test_edge_cases(raw_tennis_data):
    """Test handling of edge cases"""
    # Test with missing values
    raw_tennis_data.loc[0, 'winner_rank'] = np.nan
    raw_tennis_data.loc[1, 'loser_age'] = np.nan
    
    # Clean data
    clean_data = raw_tennis_data.dropna(subset=[
        'winner_rank', 'loser_rank',
        'winner_age', 'loser_age',
        'winner_ht', 'loser_ht'
    ])
    
    assert len(clean_data) < len(raw_tennis_data)
    assert not clean_data.isnull().any().any()

def test_feature_scaling(raw_tennis_data):
    """Test feature scaling functionality"""
    from sklearn.preprocessing import StandardScaler
    
    # Select numerical features
    numerical_features = ['winner_rank', 'loser_rank', 'winner_age', 'loser_age']
    scaler = StandardScaler()
    
    # Scale features
    scaled_features = scaler.fit_transform(raw_tennis_data[numerical_features])
    scaled_df = pd.DataFrame(
        scaled_features,
        columns=numerical_features
    )
    
    # Verify scaling
    assert abs(scaled_df.mean()).max() < 1e-10  # Close to 0
    assert abs(scaled_df.std() - 1).max() < 1e-10  # Close to 1