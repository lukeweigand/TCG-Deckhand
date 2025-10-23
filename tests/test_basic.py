"""
Basic smoke test to verify the test framework is working.
This will be replaced with real tests as we build features.
"""
import pytest


def test_python_is_working():
    """Sanity check that pytest can run."""
    assert True


def test_basic_math():
    """Another simple test to verify test discovery."""
    assert 1 + 1 == 2


def test_version_exists():
    """Check that our package has a version."""
    import src
    assert hasattr(src, '__version__')
    assert isinstance(src.__version__, str)
