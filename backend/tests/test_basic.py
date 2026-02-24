"""Basic tests for CI pipeline"""
import importlib.util


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
    required_modules = [
        "fastapi",
        "sqlalchemy", 
        "redis",
        "pydantic",
        "uvicorn",
        "psycopg2"
    ]
    
    missing = []
    for module_name in required_modules:
        spec = importlib.util.find_spec(module_name)
        if spec is None:
            missing.append(module_name)
    
    assert not missing, f"Missing dependencies: {', '.join(missing)}"