import pytest


@pytest.mark.unit
def test_backend_root_fixture_points_to_backend(backend_root):
    """Check that pytest discovers conftest.py and injects its fixture."""
    assert backend_root.is_dir()
    assert (backend_root / "app").is_dir()
