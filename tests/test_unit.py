"""
Unit tests for Tempo Craft components
"""
import pytest
from unittest.mock import Mock, patch
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.models.track import Track
from src.exceptions.track_exceptions import TrackValidationError

class TestTrack:
    """Test Track model"""
    
    def test_track_creation_valid(self):
        """Test valid track creation"""
        track = Track(
            id="test_id",
            name="Test Song",
            artist="Test Artist",
            uri="spotify:track:test_id",
            popularity=75
        )
        
        assert track.id == "test_id"
        assert track.name == "Test Song"
        assert track.artist == "Test Artist"
        assert track.uri == "spotify:track:test_id"
        assert track.popularity == 75
        assert track.bpm is None
        assert track.genres == []
        assert track.bpm_source is None
    
    def test_track_creation_invalid_popularity(self):
        """Test track creation with invalid popularity"""
        with pytest.raises(TrackValidationError):
            Track(
                id="test_id",
                name="Test Song", 
                artist="Test Artist",
                uri="spotify:track:test_id",
                popularity=150  # Invalid: > 100
            )
    
    def test_track_creation_negative_popularity(self):
        """Test track creation with negative popularity"""
        with pytest.raises(TrackValidationError):
            Track(
                id="test_id",
                name="Test Song",
                artist="Test Artist", 
                uri="spotify:track:test_id",
                popularity=-5  # Invalid: < 0
            )
    
    def test_track_set_bpm(self):
        """Test setting BPM on track"""
        track = Track(
            id="test_id",
            name="Test Song",
            artist="Test Artist",
            uri="spotify:track:test_id",
            popularity=75
        )
        
        track.bpm = 120.0
        track.bpm_source = "spotify"
        
        assert track.bpm == 120.0
        assert track.bpm_source == "spotify"

if __name__ == "__main__":
    pytest.main([__file__])
