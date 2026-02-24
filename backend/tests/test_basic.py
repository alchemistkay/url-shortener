"""Basic tests for CI pipeline"""

def test_placeholder():
    """Placeholder test to verify pytest works"""
    assert 1 + 1 == 2

def test_environment():
    """Test environment setup"""
    import sys
    assert sys.version_info.major == 3
    assert sys.version_info.minor >= 11

def test_dependencies_installed():
    """Test that required dependencies are installed"""
    try:
        import fastapi
        import sqlalchemy
        import redis
        import pydantic
        assert True
    except ImportError as e:
        assert False, f"Missing dependency: {e}"