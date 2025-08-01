"""
Spotify playlist management utilities
"""
import spotipy
import logging
from typing import List, Optional
from src.models.track import Track
from src.exceptions.spotify_exceptions import SpotifyConnectionError

logger = logging.getLogger(__name__)

class PlaylistManager:
    def __init__(self, spotify_client: spotipy.Spotify):
        self.sp = spotify_client
    
    def create_playlist(self, name: str, description: str = "", public: bool = False) -> Optional[str]:
        """Create a new playlist and return its ID"""
        try:
            user_response = self.sp.current_user()
            if not user_response or 'id' not in user_response:
                raise SpotifyConnectionError("Failed to get user information")
            
            user_id = user_response['id']
            playlist_response = self.sp.user_playlist_create(
                user=user_id, 
                name=name, 
                public=public,
                description=description
            )
            
            if not playlist_response or 'id' not in playlist_response:
                raise SpotifyConnectionError("Failed to create playlist")
            
            playlist_id = playlist_response['id']
            logger.info(f"Created playlist '{name}' with ID: {playlist_id}")
            return playlist_id
            
        except Exception as e:
            logger.error(f"Failed to create playlist '{name}': {e}")
            raise SpotifyConnectionError(f"Failed to create playlist: {e}")
    
    def add_tracks_to_playlist(self, playlist_id: str, track_uris: List[str]) -> bool:
        """Add tracks to a playlist"""
        try:
            if not track_uris:
                logger.warning("No tracks to add to playlist")
                return True
            
            # Spotify allows max 100 tracks per request
            batch_size = 100
            for i in range(0, len(track_uris), batch_size):
                batch = track_uris[i:i + batch_size]
                self.sp.playlist_add_items(playlist_id, batch)
                logger.info(f"Added {len(batch)} tracks to playlist (batch {i//batch_size + 1})")
            
            logger.info(f"Successfully added {len(track_uris)} tracks to playlist")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add tracks to playlist: {e}")
            raise SpotifyConnectionError(f"Failed to add tracks to playlist: {e}")
    
    def filter_tracks_by_bpm(self, tracks: List[Track], min_bpm: float, max_bpm: float) -> List[Track]:
        """Filter tracks by BPM range"""
        filtered = []
        for track in tracks:
            if track.bpm is not None and min_bpm <= track.bpm <= max_bpm:
                filtered.append(track)
        
        logger.info(f"Filtered {len(filtered)} tracks from {len(tracks)} by BPM range {min_bpm}-{max_bpm}")
        return filtered
    
    def filter_tracks_by_genre(self, tracks: List[Track], genre_keyword: str) -> List[Track]:
        """Filter tracks by genre keyword (case-insensitive partial match)"""
        filtered = []
        genre_keyword_lower = genre_keyword.lower()
        
        for track in tracks:
            if track.genres:
                # Check if any genre contains the keyword
                for genre in track.genres:
                    if genre_keyword_lower in genre.lower():
                        filtered.append(track)
                        break
        
        logger.info(f"Filtered {len(filtered)} tracks from {len(tracks)} by genre keyword '{genre_keyword}'")
        return filtered
    
    def filter_tracks_combined(self, tracks: List[Track], 
                             min_bpm: Optional[float] = None, 
                             max_bpm: Optional[float] = None,
                             genre_keyword: Optional[str] = None) -> List[Track]:
        """Filter tracks by multiple criteria"""
        filtered = tracks.copy()
        
        # Apply BPM filter if specified
        if min_bpm is not None and max_bpm is not None:
            filtered = self.filter_tracks_by_bpm(filtered, min_bpm, max_bpm)
        
        # Apply genre filter if specified
        if genre_keyword:
            filtered = self.filter_tracks_by_genre(filtered, genre_keyword)
        
        logger.info(f"Combined filtering result: {len(filtered)} tracks from {len(tracks)} original tracks")
        return filtered
    
    def create_bpm_playlist(self, tracks: List[Track], min_bpm: float, max_bpm: float,
                           genre_keyword: Optional[str] = None) -> Optional[str]:
        """Create a playlist based on BPM and optional genre filtering"""
        try:
            # Filter tracks
            filtered_tracks = self.filter_tracks_combined(tracks, min_bpm, max_bpm, genre_keyword)
            
            if not filtered_tracks:
                logger.warning("No tracks match the specified criteria")
                return None
            
            # Generate playlist name
            genre_part = f" - {genre_keyword.title()}" if genre_keyword else ""
            playlist_name = f"Tempo Craft {int(min_bpm)}-{int(max_bpm)} BPM{genre_part}"
            
            # Generate description
            description = f"Auto-generated playlist with BPM range {min_bpm}-{max_bpm}"
            if genre_keyword:
                description += f" and genre containing '{genre_keyword}'"
            description += f". Created by Tempo Craft. Contains {len(filtered_tracks)} tracks."
            
            # Create playlist
            playlist_id = self.create_playlist(playlist_name, description, public=False)
            if not playlist_id:
                return None
            
            # Add tracks
            track_uris = [track.uri for track in filtered_tracks]
            success = self.add_tracks_to_playlist(playlist_id, track_uris)
            
            if success:
                logger.info(f"Successfully created playlist '{playlist_name}' with {len(filtered_tracks)} tracks")
                return playlist_id
            else:
                return None
                
        except Exception as e:
            logger.error(f"Failed to create BPM playlist: {e}")
            raise SpotifyConnectionError(f"Failed to create BPM playlist: {e}")
    
    def get_playlist_url(self, playlist_id: str) -> str:
        """Get the Spotify URL for a playlist"""
        return f"https://open.spotify.com/playlist/{playlist_id}"
