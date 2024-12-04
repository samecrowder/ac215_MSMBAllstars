import sys
import os

# Adjust the path to properly import the utils module
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from utils import get_and_assert_env_var  # noqa: E402


def test_utils():
    # Test with existing env var
    os.environ["TEST_VAR"] = "test_value"
    assert get_and_assert_env_var("TEST_VAR") == "test_value"

    # Test with non-existent env var
    try:
        get_and_assert_env_var("NON_EXISTENT_VAR")
        assert False, "Should have raised ValueError"
    except ValueError:
        assert True
