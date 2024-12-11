import sys
import os

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_import_app():
    """Just try to import app.py"""
    os.environ["ENV"] = "test"  # Set test environment
    from probability_model import app  # Use absolute import

    assert app is not None
