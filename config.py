import os
from typing import Optional
from dotenv import load_dotenv

class Config:
    def __init__(self) -> None:
        # Load environment variables
        load_dotenv()
        
        # Spotify configuration
        self.client_id: Optional[str] = os.getenv('SPOTIFY_CLIENT_ID')
        self.client_secret: Optional[str] = os.getenv('SPOTIFY_CLIENT_SECRET')
        self.redirect_uri: str = os.getenv('SPOTIFY_REDIRECT_URI', 'http://localhost:8888/callback')
        self.scope: str = 'user-top-read playlist-modify-public playlist-modify-private'
        
        # GetSongBPM configuration
        self.getsongbpm_api_key: Optional[str] = os.getenv('GETSONGBPM_API_KEY')
        
        # Last.fm configuration (removed - using AcousticBrainz instead)
        # AcousticBrainz doesn't require API keys
    
    def validate(self) -> bool:
        """Validate that all required credentials are present"""
        if not all([self.client_id, self.client_secret]):
            missing = []
            if not self.client_id:
                missing.append("SPOTIFY_CLIENT_ID")
            if not self.client_secret:
                missing.append("SPOTIFY_CLIENT_SECRET")
            
            raise ValueError(f"Missing required Spotify environment variables: {', '.join(missing)}")
        
        return True
    
    def has_acousticbrainz_config(self) -> bool:
        """Check if AcousticBrainz is available (always true - no API keys needed)"""
        return True
    
    def has_getsongbpm_config(self) -> bool:
        """Check if GetSongBPM API key is configured"""
        return bool(self.getsongbpm_api_key and self.getsongbpm_api_key != 'your_api_key_here')
