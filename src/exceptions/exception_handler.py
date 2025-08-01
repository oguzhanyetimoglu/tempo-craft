"""
Exception handling utilities
"""
from src.exceptions.spotify_exceptions import SpotifyQuotaExceededError, SpotifyConnectionError, SpotifyAuthenticationError
from src.exceptions.analysis_exceptions import BPMAnalysisError, GenreAnalysisError
from src.exceptions.track_exceptions import TrackValidationError, TrackParsingError
from src.models.track import Track

class ExceptionHandler:
    """Centralized exception handling"""
    
    @staticmethod
    def handle_track_analysis(track: Track, error: Exception) -> str:
        """Handle track analysis exceptions and return user-friendly message"""
        
        if isinstance(error, SpotifyQuotaExceededError):
            return f"⏳ Quota exceeded for {track.name} - skipping BPM analysis"
        
        elif isinstance(error, BPMAnalysisError):
            return f"⚠️ BPM analysis failed for {track.name}"
        
        elif isinstance(error, GenreAnalysisError):
            return f"⚠️ Genre analysis failed for {track.name}"
        
        elif isinstance(error, TrackValidationError):
            return f"⚠️ Track validation failed for {track.name}: {error}"
        
        elif isinstance(error, TrackParsingError):
            return f"⚠️ Track parsing failed for {track.name}: {error}"
        
        else:
            return f"❌ Unexpected error analyzing {track.name}: {error}"
    
    @staticmethod
    def handle_spotify_connection(error: Exception) -> str:
        """Handle Spotify connection errors"""
        if isinstance(error, SpotifyAuthenticationError):
            return f"❌ Authentication error: {error}"
        elif isinstance(error, SpotifyConnectionError):
            return f"❌ Connection error: {error}"
        else:
            return f"❌ Error fetching tracks: {error}"
