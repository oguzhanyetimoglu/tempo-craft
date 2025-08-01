"""
Music analysis utilities
"""
import spotipy
import logging
from typing import List, Optional, Dict, Any, Tuple
from src.models.track import Track
from src.exceptions.spotify_exceptions import SpotifyQuotaExceededError
from src.exceptions.analysis_exceptions import (
    BPMAnalysisError, 
    GenreAnalysisError, 
    ExternalAPIError
)
from .acousticbrainz_analyzer import AcousticBrainzAnalyzer
from .getsongbpm_analyzer import GetSongBPMAnalyzer

logger = logging.getLogger(__name__)

class MusicAnalyzer:
    def __init__(self, spotify_client: spotipy.Spotify, 
                 acousticbrainz_analyzer: Optional[AcousticBrainzAnalyzer] = None,
                 getsongbpm_analyzer: Optional[GetSongBPMAnalyzer] = None):
        self.sp = spotify_client
        self.acousticbrainz = acousticbrainz_analyzer
        self.getsongbpm = getsongbpm_analyzer
        self.fallback_enabled = acousticbrainz_analyzer is not None or getsongbpm_analyzer is not None
    
    def get_audio_features(self, track: Track) -> bool:
        """Get BPM (tempo) for a track using Spotify API"""
        try:
            features = self.sp.audio_features([track.id])
            if features and features[0]:
                track.bpm = features[0]['tempo']
                track.bpm_source = "spotify"
                logger.info(f"Got BPM {track.bpm} for {track.name} via Spotify")
                return True
        except spotipy.exceptions.SpotifyException as e:
            if e.http_status == 403:
                raise SpotifyQuotaExceededError(f"Quota exceeded for track: {track.name}")
            else:
                raise BPMAnalysisError(f"Failed to get BPM for {track.name}: {e}")
        except Exception as e:
            raise BPMAnalysisError(f"Unexpected error getting BPM for {track.name}: {e}")
        return False
    
    def get_bpm_with_fallback(self, track: Track) -> bool:
        """Get BPM using multiple fallback sources (Spotify disabled for testing)"""
        logger.info(f"Skipping Spotify BPM (disabled), trying fallback sources for {track.name}")
        
        # Try AcousticBrainz first
        if self.acousticbrainz and self._get_bpm_from_acousticbrainz(track):
            return True
        
        # Try GetSongBPM as second fallback
        if self.getsongbpm and self._get_bpm_from_getsongbpm(track):
            return True
        
        logger.error("No BPM found from any fallback source")
        return False
    
    def _get_bpm_from_acousticbrainz(self, track: Track) -> bool:
        """Get BPM using AcousticBrainz API"""
        try:
            if not self.acousticbrainz:
                return False
            
            bpm = self.acousticbrainz.get_track_bpm(track.artist, track.name)
            if bpm:
                track.bpm = bpm
                track.bpm_source = "acousticbrainz"
                logger.info(f"Got BPM {track.bpm} for {track.name} via AcousticBrainz")
                return True
            else:
                logger.warning(f"No BPM found for {track.name} via AcousticBrainz")
                return False
        except (ExternalAPIError, BPMAnalysisError) as e:
            logger.error(f"AcousticBrainz BPM lookup failed for {track.name}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error in AcousticBrainz BPM lookup for {track.name}: {e}")
            return False

    def _get_bpm_from_getsongbpm(self, track: Track) -> bool:
        """Get BPM using GetSongBPM API"""
        try:
            if not self.getsongbpm:
                return False
            
            bpm = self.getsongbpm.get_track_bpm(track.artist, track.name)
            if bpm:
                track.bpm = bpm
                track.bpm_source = "getsongbpm"
                logger.info(f"Got BPM {track.bpm} for {track.name} via GetSongBPM")
                return True
            else:
                logger.warning(f"No BPM found for {track.name} via GetSongBPM")
                return False
        except (ExternalAPIError, BPMAnalysisError) as e:
            logger.error(f"GetSongBPM BPM lookup failed for {track.name}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error in GetSongBPM BPM lookup for {track.name}: {e}")
            return False

    def get_artist_genres(self, track: Track) -> bool:
        """Get genres from track's artist"""
        try:
            # Get first artist's genres
            results = self.sp.search(q=f"artist:{track.artist}", type="artist", limit=1)
            
            if (results and 
                'artists' in results and 
                results['artists'] and 
                'items' in results['artists'] and 
                results['artists']['items']):
                
                artist = results['artists']['items'][0]
                track.genres = artist['genres']
                return True
        except Exception as e:
            raise GenreAnalysisError(f"Failed to get genres for {track.artist}: {e}")
        return False
    
    def analyze_track(self, track: Track) -> Track:
        """Analyze a track - get BPM and genres with fallback support"""
        print(f"🔍 Analyzing: {track.name}")
        
        # Try to get BPM with fallback
        try:
            bpm_success = self.get_bpm_with_fallback(track)
            if not bpm_success:
                logger.warning(f"Could not get BPM for {track.name} from any source")
        except (SpotifyQuotaExceededError, BPMAnalysisError) as e:
            logger.error(f"BPM analysis failed for {track.name}: {e}")
            # Continue with genre analysis even if BPM fails
        
        # Try to get genres - raise exception if fails
        try:
            if not self.get_artist_genres(track):
                raise GenreAnalysisError(f"No genres found for artist: {track.artist}")
        except GenreAnalysisError:
            # Re-raise
            raise
        
        return track
    
    def analyze_tracks(self, tracks: List[Track]) -> List[Track]:
        """Analyze multiple tracks with progress reporting"""
        print(f"🔍 Analyzing {len(tracks)} tracks...")
        
        successful_tracks: List[Track] = []
        failed_tracks: List[Tuple[Track, str]] = []
        
        for i, track in enumerate(tracks, 1):
            try:
                print(f"  [{i}/{len(tracks)}] Processing: {track.name}")
                analyzed_track = self.analyze_track(track)
                successful_tracks.append(analyzed_track)
            except Exception as e:
                logger.error(f"Failed to analyze track {track.name}: {e}")
                failed_tracks.append((track, str(e)))
                # Continue with next track
        
        print(f"✅ Successfully analyzed {len(successful_tracks)} tracks")
        if failed_tracks:
            print(f"❌ Failed to analyze {len(failed_tracks)} tracks")
            for track, error in failed_tracks[:5]:  # Show first 5 failures
                print(f"   - {track.name}: {error}")
        
        return successful_tracks
    
    def get_fallback_status(self) -> Dict[str, Any]:
        """Get status of fallback services"""
        status: Dict[str, Any] = {
            'acousticbrainz_configured': self.acousticbrainz is not None,
            'acousticbrainz_available': False,
            'getsongbpm_configured': self.getsongbpm is not None,
            'getsongbpm_available': False,
            'fallback_enabled': self.fallback_enabled
        }
        
        if self.acousticbrainz:
            status['acousticbrainz_available'] = self.acousticbrainz.is_available()
        
        if self.getsongbpm:
            status['getsongbpm_available'] = self.getsongbpm.is_available()
        
        return status
