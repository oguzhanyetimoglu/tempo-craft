"""
GetSongBPM.com API integration for BPM analysis
"""
import requests
import logging
from typing import Optional
from src.exceptions.analysis_exceptions import ExternalAPIError, BPMAnalysisError

logger = logging.getLogger(__name__)

class GetSongBPMAnalyzer:
    def __init__(self, api_key: Optional[str] = None):
        self.base_url = "https://api.getsongbpm.com"
        self.api_key = api_key or "demo"  # fallback to demo key
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'TempoCraft/1.0 (Spotify Playlist Creator)'
        })
    
    def get_track_bpm(self, artist: str, track_name: str) -> Optional[float]:
        """
        Get BPM for a track using GetSongBPM.com API
        
        Args:
            artist: Artist name
            track_name: Track name
            
        Returns:
            BPM value or None if not found
            
        Raises:
            ExternalAPIError: If API request fails
            BPMAnalysisError: If BPM analysis fails
        """
        try:
            # Clean up track name and artist for better search results
            clean_artist = self._clean_search_term(artist)
            clean_track = self._clean_search_term(track_name)
            
            # Search for the track
            search_url = f"{self.base_url}/search/"
            params = {
                'api_key': self.api_key,
                'type': 'both',
                'lookup': f"{clean_artist} {clean_track}"
            }
            
            logger.info(f"Searching GetSongBPM for: {clean_artist} - {clean_track}")
            response = self.session.get(search_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'search' in data and data['search']:
                    # Look for exact or close matches
                    for result in data['search']:
                        if self._is_good_match(result, clean_artist, clean_track):
                            bpm = float(result.get('tempo', 0))
                            if bpm > 0:
                                logger.info(f"Found BPM {bpm} for {track_name} via GetSongBPM")
                                return bpm
                    
                    # If no exact match, try the first result
                    first_result = data['search'][0]
                    bpm = float(first_result.get('tempo', 0))
                    if bpm > 0:
                        logger.info(f"Found BPM {bpm} for {track_name} via GetSongBPM (first match)")
                        return bpm
                
                logger.warning(f"No BPM found for {track_name} via GetSongBPM")
                return None
                
            elif response.status_code == 429:
                logger.warning("GetSongBPM rate limit exceeded")
                raise ExternalAPIError("GetSongBPM rate limit exceeded")
            elif response.status_code == 401:
                logger.error("GetSongBPM API key invalid")
                raise ExternalAPIError("GetSongBPM API key invalid")
            else:
                logger.error(f"GetSongBPM API error: {response.status_code}")
                raise ExternalAPIError(f"GetSongBPM API returned status {response.status_code}")
                
        except requests.exceptions.Timeout:
            logger.error(f"GetSongBPM timeout for {track_name}")
            raise ExternalAPIError(f"GetSongBPM timeout for {track_name}")
        except requests.exceptions.RequestException as e:
            logger.error(f"GetSongBPM network error for {track_name}: {e}")
            raise ExternalAPIError(f"GetSongBPM network error: {e}")
        except (ValueError, KeyError) as e:
            logger.error(f"GetSongBPM data parsing error for {track_name}: {e}")
            raise BPMAnalysisError(f"Failed to parse GetSongBPM data: {e}")
        except Exception as e:
            logger.error(f"Unexpected GetSongBPM error for {track_name}: {e}")
            raise BPMAnalysisError(f"Unexpected GetSongBPM error: {e}")
    
    def _clean_search_term(self, term: str) -> str:
        """Clean search terms for better matching"""
        if not term:
            return ""
        
        # Remove common suffixes that might interfere with search
        suffixes_to_remove = [
            "- Remastered", "- Remaster", "- Remix", "- Radio Edit", 
            "- Extended", "- Original Mix", "- Radio Version", "- Album Version",
            "- Single Version", "- Bonus Track", "- Deluxe", "- Edit"
        ]
        
        cleaned = term.strip()
        for suffix in suffixes_to_remove:
            if cleaned.endswith(suffix):
                cleaned = cleaned[:-len(suffix)].strip()
        
        # Remove extra whitespace and special characters that might cause issues
        cleaned = ' '.join(cleaned.split())
        
        return cleaned
    
    def _is_good_match(self, result: dict, target_artist: str, target_track: str) -> bool:
        """Check if the search result is a good match for the target"""
        result_artist = result.get('artist', {}).get('name', '').lower()
        result_song = result.get('song', {}).get('title', '').lower()
        
        target_artist_lower = target_artist.lower()
        target_track_lower = target_track.lower()
        
        # Check for artist match (partial match is OK)
        artist_match = (
            target_artist_lower in result_artist or 
            result_artist in target_artist_lower or
            self._similarity_score(target_artist_lower, result_artist) > 0.7
        )
        
        # Check for track match (partial match is OK)
        track_match = (
            target_track_lower in result_song or 
            result_song in target_track_lower or
            self._similarity_score(target_track_lower, result_song) > 0.7
        )
        
        return artist_match and track_match
    
    def _similarity_score(self, str1: str, str2: str) -> float:
        """Simple similarity score between two strings"""
        if not str1 or not str2:
            return 0.0
        
        # Simple character-based similarity
        set1 = set(str1.lower().replace(' ', ''))
        set2 = set(str2.lower().replace(' ', ''))
        
        if not set1 or not set2:
            return 0.0
        
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        return intersection / union if union > 0 else 0.0
    
    def is_available(self) -> bool:
        """Check if GetSongBPM API is available"""
        try:
            test_url = f"{self.base_url}/search/"
            params = {
                'api_key': self.api_key,
                'type': 'song',
                'lookup': 'test'
            }
            response = self.session.get(test_url, params=params, timeout=5)
            return response.status_code in [200, 404]  # 404 is OK, means API is up but no results
        except Exception:
            return False
