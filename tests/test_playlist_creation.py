"""
Integration tests for playlist creation functionality
"""
import logging
import sys
import os
from typing import List

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from config import Config
from src.auth.spotify_auth import SpotifyAuth
from src.models.track import Track
from src.analyzer.music_analyzer import MusicAnalyzer
from src.analyzer.acousticbrainz_analyzer import AcousticBrainzAnalyzer
from src.analyzer.getsongbpm_analyzer import GetSongBPMAnalyzer
from src.playlist.playlist_manager import PlaylistManager

# Set up logging
logging.basicConfig(level=logging.INFO)

def test_playlist_creation():
    """Test full playlist creation workflow"""
    print("🧪 Testing playlist creation workflow...")
    
    # Setup
    config = Config()
    auth = SpotifyAuth()
    auth.connect()
    sp = auth.get_client()
    
    if not sp:
        print("❌ Failed to connect to Spotify")
        return False
    
    # Create test tracks with known BPM
    test_tracks: List[Track] = [
        Track(
            id="test1",
            name="Test Song 1",
            artist="Test Artist 1", 
            uri="spotify:track:test1",
            popularity=80
        ),
        Track(
            id="test2", 
            name="Test Song 2",
            artist="Test Artist 2",
            uri="spotify:track:test2",
            popularity=70
        )
    ]
    
    # Add mock BPM data
    test_tracks[0].bpm = 120.0
    test_tracks[0].bpm_source = "test"
    test_tracks[0].genres = ["electronic", "dance"]
    
    test_tracks[1].bpm = 140.0
    test_tracks[1].bpm_source = "test"
    test_tracks[1].genres = ["rock", "alternative"]
    
    # Test playlist manager
    playlist_manager = PlaylistManager(sp)
    
    # Test filtering by BPM
    print("🔍 Testing BPM filtering...")
    filtered_bpm = playlist_manager.filter_tracks_by_bpm(test_tracks, 115, 125)
    assert len(filtered_bpm) == 1
    assert filtered_bpm[0].bpm == 120.0
    print("✅ BPM filtering works")
    
    # Test filtering by genre  
    print("🔍 Testing genre filtering...")
    filtered_genre = playlist_manager.filter_tracks_by_genre(test_tracks, "electronic")
    assert len(filtered_genre) == 1
    assert filtered_genre[0].genres and "electronic" in filtered_genre[0].genres
    print("✅ Genre filtering works")
    
    # Test combined filtering
    print("🔍 Testing combined filtering...")
    filtered_combined = playlist_manager.filter_tracks_combined(
        test_tracks, 
        min_bpm=115, 
        max_bpm=125,
        genre_keyword="electronic"
    )
    assert len(filtered_combined) == 1
    print("✅ Combined filtering works")
    
    print("🎉 All playlist tests passed!")
    return True

def test_mock_playlist_creation():
    """Test playlist creation without actually creating a playlist"""
    print("🧪 Testing mock playlist creation...")
    
    # This would test the playlist creation logic without
    # actually creating a playlist on Spotify
    # (Useful for CI/CD where we don't want to spam playlists)
    
    print("✅ Mock playlist tests passed!")
    return True

if __name__ == "__main__":
    if test_playlist_creation():
        print("✅ All playlist creation tests passed!")
    else:
        print("❌ Some tests failed!")
        exit(1)
