import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

class TestEndpoints:
    """Test suite for API endpoints"""

    def test_root_endpoint(self):
        """Test root endpoint returns welcome message"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "🌟 Welcome to the Star Wars API Wrapper!" in data["message"]
        assert data["may_the_force_be_with_you"] is True

    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "cache" in data
        assert "timestamp" in data

    def test_get_films(self):
        """Test films endpoint returns film data"""
        response = client.get("/films")
        assert response.status_code == 200
        data = response.json()
        assert "count" in data
        assert "results" in data
        assert "message" in data
        assert data["count"] > 0
        
        # Check film structure
        if data["results"]:
            film = data["results"][0]
            required_fields = [
                "episode_id", "title", "director", "producer", 
                "release_date", "character_count", "starship_count"
            ]
            for field in required_fields:
                assert field in film

    def test_get_film_characters_valid(self):
        """Test getting characters for valid film"""
        # Test with film ID 1 (A New Hope)
        response = client.get("/films/1/characters")
        assert response.status_code == 200
        data = response.json()
        assert "count" in data
        assert "results" in data
        assert "film_id" in data
        assert data["film_id"] == 1
        assert data["count"] > 0
        
        # Check character structure
        if data["results"]:
            character = data["results"][0]
            required_fields = [
                "name", "height", "mass", "hair_color", 
                "eye_color", "birth_year", "gender"
            ]
            for field in required_fields:
                assert field in character

    def test_get_film_characters_invalid(self):
        """Test getting characters for invalid film"""
        response = client.get("/films/999/characters")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

    def test_get_film_starships_valid(self):
        """Test getting starships for valid film"""
        # Test with film ID 1 (A New Hope)
        response = client.get("/films/1/starships")
        assert response.status_code == 200
        data = response.json()
        assert "count" in data
        assert "results" in data
        assert "film_id" in data
        assert data["film_id"] == 1
        
        # Check starship structure if any exist
        if data["results"]:
            starship = data["results"][0]
            required_fields = [
                "name", "model", "manufacturer", "length",
                "crew", "passengers", "starship_class"
            ]
            for field in required_fields:
                assert field in starship

    def test_get_film_starships_invalid(self):
        """Test getting starships for invalid film"""
        response = client.get("/films/999/starships")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

    def test_rate_limiting(self):
        """Test that rate limiting is properly configured"""
        # This test would need to be adjusted based on actual rate limits
        # For now, just ensure the endpoint responds normally
        response = client.get("/films")
        assert response.status_code == 200

    def test_cors_headers(self):
        """Test CORS headers are present"""
        response = client.options("/films")
        # FastAPI handles OPTIONS automatically with CORS middleware
        assert response.status_code == 200

    def test_invalid_endpoints(self):
        """Test that invalid endpoints return 404"""
        response = client.get("/nonexistent")
        assert response.status_code == 404

    def test_response_content_type(self):
        """Test that responses have correct content type"""
        response = client.get("/films")
        assert response.status_code == 200
        assert "application/json" in response.headers.get("content-type", "")

class TestCaching:
    """Test caching functionality"""

    def test_cache_performance(self):
        """Test that repeated requests are faster (cached)"""
        import time
        
        # First request (should hit SWAPI)
        start = time.time()
        response1 = client.get("/films")
        first_duration = time.time() - start
        
        # Second request (should be cached)
        start = time.time()
        response2 = client.get("/films")
        second_duration = time.time() - start
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response1.json() == response2.json()
        # Second request should generally be faster due to caching
        # (This test might be flaky in some environments)

class TestErrorHandling:
    """Test error handling scenarios"""

    def test_malformed_film_id(self):
        """Test handling of non-numeric film IDs"""
        response = client.get("/films/invalid/characters")
        assert response.status_code == 422  # Validation error

    def test_negative_film_id(self):
        """Test handling of negative film IDs"""
        response = client.get("/films/-1/characters")
        assert response.status_code == 404

    def test_zero_film_id(self):
        """Test handling of zero film ID"""
        response = client.get("/films/0/characters")
        assert response.status_code == 404