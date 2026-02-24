"""Integration tests for URL Shortener API"""

import requests
import pytest
import time

BASE_URL = "http://localhost:8000"


class TestHealthEndpoint:
    """Test health check endpoint"""
    
    def test_health_check(self):
        """Health endpoint returns healthy status"""
        response = requests.get(f"{BASE_URL}/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "dependencies" in data
        assert data["dependencies"]["database"] == "healthy"
        assert data["dependencies"]["cache"] == "healthy"


class TestURLShortening:
    """Test URL shortening functionality"""
    
    def test_shorten_random_url(self):
        """Create URL with random short code"""
        payload = {"original_url": "https://example.com"}
        response = requests.post(f"{BASE_URL}/api/v1/shorten", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert "short_code" in data
        assert data["original_url"] == "https://example.com/"
        assert "short_url" in data
        assert data["clicks"] == 0
    
    def test_shorten_custom_slug(self):
        """Create URL with custom slug"""
        payload = {
            "original_url": "https://github.com",
            "custom_slug": f"test-{int(time.time())}"
        }
        response = requests.post(f"{BASE_URL}/api/v1/shorten", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["short_code"] == payload["custom_slug"]
        assert data["original_url"] == "https://github.com/"
    
    def test_duplicate_custom_slug(self):
        """Duplicate custom slug returns error"""
        slug = f"duplicate-{int(time.time())}"
        payload = {"original_url": "https://example.com", "custom_slug": slug}
        
        # First request succeeds
        response1 = requests.post(f"{BASE_URL}/api/v1/shorten", json=payload)
        assert response1.status_code == 200
        
        # Second request with same slug fails
        response2 = requests.post(f"{BASE_URL}/api/v1/shorten", json=payload)
        assert response2.status_code == 400
    
    def test_invalid_url(self):
        """Invalid URL returns error"""
        payload = {"original_url": "not-a-valid-url"}
        response = requests.post(f"{BASE_URL}/api/v1/shorten", json=payload)
        assert response.status_code == 422


class TestRedirect:
    """Test URL redirect functionality"""
    
    def setup_method(self):
        """Create a test URL before each test"""
        self.test_slug = f"redirect-{int(time.time())}"
        payload = {
            "original_url": "https://example.com",
            "custom_slug": self.test_slug
        }
        requests.post(f"{BASE_URL}/api/v1/shorten", json=payload)
    
    def test_redirect_works(self):
        """Short URL redirects to original"""
        response = requests.get(
            f"{BASE_URL}/{self.test_slug}",
            allow_redirects=False
        )
        assert response.status_code == 307
        assert "location" in response.headers
        assert response.headers["location"] == "https://example.com/"
    
    def test_redirect_increments_clicks(self):
        """Redirect increments click count"""
        # Get initial clicks
        stats1 = requests.get(f"{BASE_URL}/api/v1/stats/{self.test_slug}")
        initial_clicks = stats1.json()["total_clicks"]
        
        # Click the URL
        requests.get(f"{BASE_URL}/{self.test_slug}", allow_redirects=False)
        
        # Check clicks increased
        stats2 = requests.get(f"{BASE_URL}/api/v1/stats/{self.test_slug}")
        new_clicks = stats2.json()["total_clicks"]
        assert new_clicks == initial_clicks + 1
    
    def test_nonexistent_code_404(self):
        """Non-existent short code returns 404"""
        response = requests.get(f"{BASE_URL}/nonexistent123")
        assert response.status_code == 404


class TestStats:
    """Test statistics endpoint"""
    
    def setup_method(self):
        """Create a test URL before each test"""
        self.test_slug = f"stats-{int(time.time())}"
        payload = {
            "original_url": "https://example.com",
            "custom_slug": self.test_slug
        }
        requests.post(f"{BASE_URL}/api/v1/shorten", json=payload)
    
    def test_stats_endpoint(self):
        """Stats endpoint returns correct data"""
        response = requests.get(f"{BASE_URL}/api/v1/stats/{self.test_slug}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["short_code"] == self.test_slug
        assert data["original_url"] == "https://example.com/"
        assert data["total_clicks"] >= 0
        assert data["is_active"] is True
    
    def test_stats_nonexistent(self):
        """Stats for non-existent URL returns 404"""
        response = requests.get(f"{BASE_URL}/api/v1/stats/nonexistent")
        assert response.status_code == 404


class TestCache:
    """Test Redis caching functionality"""
    
    def test_cache_stats_endpoint(self):
        """Cache stats endpoint works"""
        response = requests.get(f"{BASE_URL}/api/v1/cache/stats")
        assert response.status_code == 200
        
        data = response.json()
        assert "total_keys" in data
        assert "hits" in data
        assert "misses" in data
    
    def test_cache_hit_after_redirect(self):
        """Second redirect uses cache"""
        # Create URL
        slug = f"cache-{int(time.time())}"
        payload = {"original_url": "https://example.com", "custom_slug": slug}
        requests.post(f"{BASE_URL}/api/v1/shorten", json=payload)
        
        # Get initial cache stats
        stats1 = requests.get(f"{BASE_URL}/api/v1/cache/stats").json()
        initial_hits = stats1.get("hits", 0)
        
        # First redirect (cache miss)
        requests.get(f"{BASE_URL}/{slug}", allow_redirects=False)
        
        # Second redirect (cache hit)
        requests.get(f"{BASE_URL}/{slug}", allow_redirects=False)
        
        # Check cache hits increased
        stats2 = requests.get(f"{BASE_URL}/api/v1/cache/stats").json()
        new_hits = stats2.get("hits", 0)
        assert new_hits > initial_hits


class TestMetrics:
    """Test Prometheus metrics endpoint"""
    
    def test_metrics_endpoint(self):
        """Metrics endpoint returns Prometheus format"""
        response = requests.get(f"{BASE_URL}/metrics")
        assert response.status_code == 200
        assert "urlshortener" in response.text
        assert "http_requests_total" in response.text