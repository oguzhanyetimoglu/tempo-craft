"""
AcousticBrainz API integration for BPM and audio feature analysis.
Provides fallback functionality when Spotify API quota is exceeded.
"""

import requests
import logging
from typing import Optional, Dict, Any, Union
from ..exceptions.analysis_exceptions import (
    BPMAnalysisError, 
    ExternalAPIError, 
    DataNotFoundError
)

logger = logging.getLogger(__name__)

class AcousticBrainzAnalyzer:
    """Handles BPM analysis using AcousticBrainz API as fallback"""
    
    def __init__(self) -> None:
        """
        Initialize AcousticBrainz analyzer
        
        AcousticBrainz doesn't require API keys - it's a free service
        """
        self.base_url = "https://acousticbrainz.org"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'TempoCraft/1.0 (BPM Analysis Tool)'
        })
    
    def get_track_bpm_by_mbid(self, mbid: str) -> Optional[float]:
        """
        Get BPM for a track using MusicBrainz ID (MBID)
        
        Args:
            mbid: MusicBrainz ID for the track
            
        Returns:
            BPM value if found, None otherwise
            
        Raises:
            ExternalAPIError: If API request fails
            DataNotFoundError: If track not found
        """
        try:
            # Try high-level data first (more reliable)
            url = f"{self.base_url}/{mbid}/high-level"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                bpm = self._extract_bpm_from_highlevel(data)
                if bpm:
                    logger.info(f"Found BPM {bpm} for MBID {mbid} via AcousticBrainz high-level")
                    return bpm
            
            # Try low-level data as fallback
            url = f"{self.base_url}/{mbid}/low-level"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                bpm = self._extract_bpm_from_lowlevel(data)
                if bpm:
                    logger.info(f"Found BPM {bpm} for MBID {mbid} via AcousticBrainz low-level")
                    return bpm
            elif response.status_code == 404:
                raise DataNotFoundError(f"Track with MBID {mbid} not found in AcousticBrainz")
            else:
                raise ExternalAPIError(f"AcousticBrainz API error: {response.status_code}")
            
            logger.warning(f"No BPM found for MBID {mbid} in AcousticBrainz")
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error accessing AcousticBrainz: {e}")
            raise ExternalAPIError(f"Failed to connect to AcousticBrainz: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error getting BPM from AcousticBrainz: {e}")
            raise BPMAnalysisError(f"Failed to analyze BPM via AcousticBrainz: {str(e)}")
    
    def search_mbid_by_track(self, artist: str, track_name: str) -> Optional[str]:
        """
        Search for MusicBrainz ID using artist and track name
        
        Args:
            artist: Artist name
            track_name: Track name
            
        Returns:
            MusicBrainz ID if found, None otherwise
        """
        try:
            # Use MusicBrainz search API
            search_url = "https://musicbrainz.org/ws/2/recording"
            params = {
                'query': f'artist:"{artist}" AND recording:"{track_name}"',
                'fmt': 'json',
                'limit': 5
            }
            
            response = self.session.get(search_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                recordings = data.get('recordings', [])
                
                for recording in recordings:
                    # Get the best match (first result is usually most accurate)
                    mbid = recording.get('id')
                    if mbid:
                        logger.info(f"Found MBID {mbid} for {artist} - {track_name}")
                        return mbid
            
            logger.warning(f"No MBID found for {artist} - {track_name}")
            return None
            
        except Exception as e:
            logger.error(f"Error searching MBID: {e}")
            return None
    
    def get_track_bpm(self, artist: str, track_name: str) -> Optional[float]:
        """
        Get BPM for a track using artist and track name
        
        Args:
            artist: Artist name
            track_name: Track name
            
        Returns:
            BPM value if found, None otherwise
        """
        # First, find the MusicBrainz ID
        mbid = self.search_mbid_by_track(artist, track_name)
        if not mbid:
            return None
        
        # Then get BPM using the MBID
        return self.get_track_bpm_by_mbid(mbid)
    
    def _extract_bpm_from_highlevel(self, data: Dict[str, Any]) -> Optional[float]:
        """Extract BPM from high-level AcousticBrainz data"""
        try:
            # High-level data contains rhythm descriptors
            rhythm = data.get('rhythm', {})
            
            # Look for BPM in various fields
            bpm_fields = ['bpm', 'tempo', 'rhythm.bpm']
            
            for field in bpm_fields:
                if '.' in field:
                    # Nested field access
                    parts = field.split('.')
                    value = data
                    for part in parts:
                        value = value.get(part, {})
                    if isinstance(value, (int, float)) and 60 <= value <= 200:
                        return float(value)
                else:
                    # Direct field access
                    value = rhythm.get(field)
                    if isinstance(value, (int, float)) and 60 <= value <= 200:
                        return float(value)
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting BPM from high-level data: {e}")
            return None
    
    def _extract_bpm_from_lowlevel(self, data: Dict[str, Any]) -> Optional[float]:
        """Extract BPM from low-level AcousticBrainz data"""
        try:
            # Low-level data contains detailed rhythm analysis
            rhythm = data.get('rhythm', {})
            
            # Try various BPM fields in low-level data
            bpm_candidates = []
            
            # Check for tempo estimates
            if 'tempo' in rhythm:
                tempo = rhythm['tempo']
                if isinstance(tempo, dict):
                    # Multiple tempo estimates
                    for key, value in tempo.items():
                        if isinstance(value, (int, float)) and 60 <= value <= 200:
                            bpm_candidates.append(float(value))
                elif isinstance(tempo, (int, float)) and 60 <= tempo <= 200:
                    bpm_candidates.append(float(tempo))
            
            # Check for BPM field
            if 'bpm' in rhythm:
                bpm = rhythm['bpm']
                if isinstance(bpm, (int, float)) and 60 <= bpm <= 200:
                    bpm_candidates.append(float(bpm))
            
            # Return the first valid BPM found
            if bpm_candidates:
                return bpm_candidates[0]
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting BPM from low-level data: {e}")
            return None
    
    def get_track_info(self, artist: str, track_name: str) -> Dict[str, Any]:
        """
        Get comprehensive track information from AcousticBrainz
        
        Args:
            artist: Artist name
            track_name: Track name
            
        Returns:
            Dictionary with track information
        """
        try:
            mbid = self.search_mbid_by_track(artist, track_name)
            if not mbid:
                return {
                    'artist': artist,
                    'track': track_name,
                    'error': 'MBID not found'
                }
            
            info: Dict[str, Union[str, float, None]] = {
                'artist': artist,
                'track': track_name,
                'mbid': mbid,
                'bpm': None,
                'key': None,
                'mood': None,
                'danceability': None,
                'energy': None
            }
            
            # Try to get high-level data
            try:
                url = f"{self.base_url}/{mbid}/high-level"
                response = self.session.get(url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    info['bpm'] = self._extract_bpm_from_highlevel(data)
                    
                    # Extract additional features
                    if 'mood' in data:
                        info['mood'] = data['mood']
                    if 'danceability' in data:
                        info['danceability'] = data['danceability']
            except Exception:
                pass
            
            # Try to get low-level data if high-level failed
            if not info['bpm']:
                try:
                    url = f"{self.base_url}/{mbid}/low-level"
                    response = self.session.get(url, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        info['bpm'] = self._extract_bpm_from_lowlevel(data)
                except Exception:
                    pass
            
            return info
            
        except Exception as e:
            logger.warning(f"Could not get track info from AcousticBrainz: {e}")
            return {
                'artist': artist,
                'track': track_name,
                'error': str(e)
            }
    
    def is_available(self) -> bool:
        """Check if AcousticBrainz API is available and accessible"""
        try:
            # Test with a well-known track MBID
            test_url = f"{self.base_url}/5b11f4ce-a62d-471e-81fc-a69a8278c7da/high-level"
            response = self.session.get(test_url, timeout=5)
            return response.status_code in [200, 404]  # 404 is ok, means service is up
        except Exception:
            return False
