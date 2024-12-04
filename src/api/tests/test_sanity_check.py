from ..utils import get_project_root, get_data_folder


def test_true():
    assert True


def test_addition():
    assert 1 + 1 == 2


def test_utils():
    # Test get_project_root
    root = get_project_root()
    assert isinstance(root, str)
    assert len(root) > 0

    # Test get_data_folder
    data_folder = get_data_folder()
    assert isinstance(data_folder, str)
    assert len(data_folder) > 0
