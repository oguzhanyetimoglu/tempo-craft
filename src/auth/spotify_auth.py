"""
Spotify authentication module
"""
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import requests
from config import Config
from src.exceptions.spotify_exceptions import (
    SpotifyConnectionError, 
    SpotifyAuthenticationError
)

class SpotifyAuth:
    def __init__(self):
        self.config = Config()
        self.config.validate()
        self.sp = None
    
    def connect(self):
        """Connect to Spotify API"""
        print("🎵 Connecting to Spotify...")
        
        try:
            self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
                client_id=self.config.client_id,
                client_secret=self.config.client_secret,
                redirect_uri=self.config.redirect_uri,
                scope=self.config.scope,
                open_browser=True,
                cache_path=".cache"
            ))
            
            user_info = self.sp.current_user()
            if user_info and 'display_name' in user_info:
                print(f"✅ Connected successfully: {user_info['display_name']}")
            else:
                print("✅ Connected successfully!")
            return True
            
        except spotipy.SpotifyException as e:
            raise SpotifyAuthenticationError(f"Spotify authentication failed: {e}")
        except requests.ConnectionError as e:
            raise SpotifyConnectionError(f"Network connection failed: {e}")
        except Exception as e:
            raise SpotifyConnectionError(f"Unexpected connection error: {e}")
    
    def get_client(self):
        """Get the Spotify client"""
        return self.sp
