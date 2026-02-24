"""Pytest configuration for integration tests"""

import pytest
import time


@pytest.fixture(scope="session", autouse=True)
def wait_for_api():
    """Wait for API to be ready before running tests"""
    import requests
    max_retries = 30
    
    for i in range(max_retries):
        try:
            response = requests.get("http://localhost:8000/api/v1/health", timeout=2)
            if response.status_code == 200:
                print("\nAPI is ready!")
                return
        except Exception:
            if i < max_retries - 1:
                time.sleep(1)
            else:
                raise Exception("API failed to start in time")
    
    raise Exception("API not responding")