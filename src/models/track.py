"""
Track data model
"""
from dataclasses import dataclass
from typing import List, Optional
from src.exceptions.track_exceptions import TrackValidationError

@dataclass
class Track:
    """Represents a music track with its metadata"""
    id: str
    name: str
    artist: str
    uri: str
    popularity: int
    bpm: Optional[float] = None
    genres: Optional[List[str]] = None
    bpm_source: Optional[str] = None  # Track where BPM data came from (spotify, lastfm, etc.)
    
    def __post_init__(self):
        if self.genres is None:
            self.genres = []
        
        # Validate required fields
        if not self.id or not self.id.strip():
            raise TrackValidationError("Track ID cannot be empty")
        
        if not self.name or not self.name.strip():
            raise TrackValidationError("Track name cannot be empty")
        
        if not self.artist or not self.artist.strip():
            raise TrackValidationError("Track artist cannot be empty")
        
        if not self.uri or not self.uri.strip():
            raise TrackValidationError("Track URI cannot be empty")
        
        if self.popularity < 0 or self.popularity > 100:
            raise TrackValidationError("Track popularity must be between 0 and 100")
    
    def __str__(self) -> str:
        return f"{self.artist} - {self.name}"
