from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def backend_root() -> Path:
    """Return the backend directory for tests that need project-relative paths."""
    return Path(__file__).resolve().parents[1]
