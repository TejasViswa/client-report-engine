"""Pytest configuration and fixtures."""

import json
import pytest
from pathlib import Path


@pytest.fixture
def project_root():
    """Return the project root directory."""
    return Path(__file__).resolve().parents[1]


@pytest.fixture
def sample_data(project_root):
    """Load sample client data."""
    data_file = project_root / "data" / "sample_client.json"
    if data_file.exists():
        with open(data_file, "r") as f:
            return json.load(f)
    return {}


@pytest.fixture
def template_dir(project_root):
    """Return template directory path."""
    return project_root / "reports" / "templates"


@pytest.fixture
def output_dir(project_root):
    """Return output directory path."""
    return project_root / "reports" / "output"

