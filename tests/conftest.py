import os
import pytest
import tempfile
import yaml
from pathlib import Path


@pytest.fixture
def templates_dir():
    """Provide the templates directory path."""
    return os.path.join(os.path.dirname(__file__), '..', 'playbook_generator', 'templates')


@pytest.fixture
def fixtures_dir():
    """Provide the fixtures directory path."""
    return os.path.join(os.path.dirname(__file__), 'fixtures')


@pytest.fixture
def temp_output_dir():
    """Provide a temporary directory for test outputs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def basic_params(fixtures_dir):
    """Load basic parameters fixture."""
    with open(os.path.join(fixtures_dir, 'basic_params.yaml'), 'r') as f:
        return yaml.safe_load(f)


@pytest.fixture
def with_tasks_params(fixtures_dir):
    """Load with_tasks parameters fixture."""
    with open(os.path.join(fixtures_dir, 'with_tasks_params.yaml'), 'r') as f:
        return yaml.safe_load(f)


@pytest.fixture
def conditional_params(fixtures_dir):
    """Load conditional parameters fixture."""
    with open(os.path.join(fixtures_dir, 'conditional_params.yaml'), 'r') as f:
        return yaml.safe_load(f)
