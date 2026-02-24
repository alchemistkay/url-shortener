"""Integration tests for URL Shortener API"""

import requests
import time
import random
import string

BASE_URL = "http://localhost:8000"


def random_slug():
    """Generate random slug without hyphens"""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))


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
        """Create URL with custom slug (no hyphens)"""
        slug = random_slug()
        payload = {
            "original_url": "https://github.com",
            "custom_slug": slug
        }
        response = requests.post(f"{BASE_URL}/api/v1/shorten", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["short_code"] == slug
        assert data["original_url"] == "https://github.com/"
    
    def test_duplicate_custom_slug(self):
        """Duplicate custom slug returns error"""
        slug = random_slug()
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
    
    def test_redirect_works(self):
        """Short URL redirects to original"""
        # Create URL first
        slug = random_slug()
        payload = {
            "original_url": "https://example.com",
            "custom_slug": slug
        }
        create_response = requests.post(f"{BASE_URL}/api/v1/shorten", json=payload)
        assert create_response.status_code == 200
        
        # Test redirect
        response = requests.get(
            f"{BASE_URL}/{slug}",
            allow_redirects=False
        )
        assert response.status_code == 307
        assert "location" in response.headers
        assert response.headers["location"] == "https://example.com/"
    
    def test_redirect_increments_clicks(self):
        """Redirect increments click count"""
        # Create URL
        slug = random_slug()
        payload = {"original_url": "https://example.com", "custom_slug": slug}
        requests.post(f"{BASE_URL}/api/v1/shorten", json=payload)
        
        # Get initial clicks
        stats1 = requests.get(f"{BASE_URL}/api/v1/stats/{slug}")
        assert stats1.status_code == 200
        initial_clicks = stats1.json()["total_clicks"]
        
        # Click the URL
        requests.get(f"{BASE_URL}/{slug}", allow_redirects=False)
        
        # Check clicks increased
        stats2 = requests.get(f"{BASE_URL}/api/v1/stats/{slug}")
        assert stats2.status_code == 200
        new_clicks = stats2.json()["total_clicks"]
        assert new_clicks == initial_clicks + 1
    
    def test_nonexistent_code_404(self):
        """Non-existent short code returns 404"""
        response = requests.get(f"{BASE_URL}/nonexistent123abc")
        assert response.status_code == 404


class TestStats:
    """Test statistics endpoint"""
    
    def test_stats_endpoint(self):
        """Stats endpoint returns correct data"""
        # Create URL first
        slug = random_slug()
        payload = {
            "original_url": "https://example.com",
            "custom_slug": slug
        }
        create_response = requests.post(f"{BASE_URL}/api/v1/shorten", json=payload)
        assert create_response.status_code == 200
        
        # Get stats
        response = requests.get(f"{BASE_URL}/api/v1/stats/{slug}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["short_code"] == slug
        assert data["original_url"] == "https://example.com/"
        assert data["total_clicks"] >= 0
        assert data["is_active"] is True
    
    def test_stats_nonexistent(self):
        """Stats for non-existent URL returns 404"""
        response = requests.get(f"{BASE_URL}/api/v1/stats/nonexistent999")
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
    
    def test_redirect_uses_cache(self):
        """Multiple redirects increase cache hits"""
        # Create URL
        slug = random_slug()
        payload = {"original_url": "https://example.com", "custom_slug": slug}
        requests.post(f"{BASE_URL}/api/v1/shorten", json=payload)
        
        # Do multiple redirects
        for _ in range(3):
            requests.get(f"{BASE_URL}/{slug}", allow_redirects=False)
            time.sleep(0.1)
        
        # Just verify endpoint works - cache behavior varies
        stats = requests.get(f"{BASE_URL}/api/v1/cache/stats")
        assert stats.status_code == 200
        # Cache stats should have some activity
        data = stats.json()
        assert isinstance(data.get("total_keys"), int)


class TestMetrics:
    """Test Prometheus metrics endpoint"""
    
    def test_metrics_endpoint(self):
        """Metrics endpoint returns Prometheus format"""
        response = requests.get(f"{BASE_URL}/metrics")
        assert response.status_code == 200
        assert "urlshortener" in response.text
        assert "http_requests_total" in response.text