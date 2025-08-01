"""
Spotify API related exceptions
"""
from . import TempoCraftError

class SpotifyError(TempoCraftError):
    """Base Spotify API error"""
    pass

class SpotifyConnectionError(SpotifyError):
    """Failed to connect to Spotify"""
    pass

class SpotifyAuthenticationError(SpotifyError):
    """Authentication failed"""
    pass

class SpotifyQuotaExceededError(SpotifyError):
    """API quota exceeded (403 error)"""
    pass

class SpotifyTrackNotFoundError(SpotifyError):
    """Track not found on Spotify"""
    pass
