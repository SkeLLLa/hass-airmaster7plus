"""Test fixtures for the AM7P integration."""

from pathlib import Path
import sys

import pytest

# Ensure `custom_components` is importable in CI test environments.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable loading of custom integrations in all tests."""
    yield
