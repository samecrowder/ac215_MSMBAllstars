import os
import sys
from dotenv import load_dotenv

# Add the parent directory to PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load test environment variables
def pytest_configure(config):
    """Set up test environment"""
    env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env.test')
    load_dotenv(env_file)
    
    # Set default environment variables for testing
    os.environ.setdefault('LOOKBACK', '5')
