"""
Track data related exceptions
"""
from . import TempoCraftError

class TrackError(TempoCraftError):
    """Base track error"""
    pass

class TrackValidationError(TrackError):
    """Track data validation failed"""
    pass

class TrackParsingError(TrackError):
    """Failed to parse track data from Spotify response"""
    pass
