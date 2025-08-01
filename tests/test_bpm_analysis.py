"""
Test BPM analysis without playlist creation
"""
import logging
from config import Config
from src.auth.spotify_auth import SpotifyAuth
from src.models.track import Track
from src.analyzer.music_analyzer import MusicAnalyzer
from src.analyzer.acousticbrainz_analyzer import AcousticBrainzAnalyzer
from src.analyzer.getsongbpm_analyzer import GetSongBPMAnalyzer

# Set up logging to see debug messages
logging.basicConfig(level=logging.DEBUG)

def test_bpm_analysis():
    print("🔧 Setting up...")
    
    # Initialize configuration and auth
    config = Config()
    auth = SpotifyAuth()
    auth.connect()
    sp = auth.get_client()
    
    if not sp:
        print("❌ Failed to connect to Spotify")
        return
    
    # Create analyzers
    acousticbrainz_analyzer = AcousticBrainzAnalyzer()
    getsongbpm_analyzer = GetSongBPMAnalyzer(config.getsongbpm_api_key)
    analyzer = MusicAnalyzer(sp, acousticbrainz_analyzer, getsongbpm_analyzer)
    
    print("🎵 Getting 5 top tracks...")
    top_tracks_response = sp.current_user_top_tracks(limit=5)
    if not top_tracks_response or 'items' not in top_tracks_response:
        print("❌ Failed to retrieve top tracks")
        return
    top_tracks = top_tracks_response['items']
    
    print("📝 Parsing tracks...")
    tracks = []
    for spotify_track in top_tracks:
        track = Track(
            id=spotify_track['id'],
            name=spotify_track['name'],
            artist=spotify_track['artists'][0]['name'],
            uri=spotify_track['uri'],
            popularity=spotify_track['popularity']
        )
        tracks.append(track)
    
    print("🔍 Analyzing BPM...")
    analyzed_tracks = analyzer.analyze_tracks(tracks)
    
    # Show results
    print("\n📊 BPM Analysis Results:")
    for track in analyzed_tracks:
        bpm_info = f"BPM: {track.bpm}" if track.bpm else "BPM: Not found"
        source_info = f"(from {track.bpm_source})" if track.bpm_source else ""
        print(f"  • {track.artist} - {track.name}: {bpm_info} {source_info}")
    
    # Summary
    total_tracks = len(analyzed_tracks)
    bpm_tracks = [t for t in analyzed_tracks if t.bpm is not None]
    spotify_bpm = [t for t in bpm_tracks if t.bpm_source == "spotify"]
    acousticbrainz_bpm = [t for t in bpm_tracks if t.bpm_source == "acousticbrainz"]
    getsongbpm_bpm = [t for t in bpm_tracks if t.bpm_source == "getsongbpm"] 
       
    print(f"\n📊 Summary:")
    print(f"  Total tracks: {total_tracks}")
    print(f"  With BPM: {len(bpm_tracks)}")
    print(f"  From Spotify: {len(spotify_bpm)}")
    print(f"  From AcousticBrainz: {len(acousticbrainz_bpm)}")
    print(f"  From GetSongBPM: {len(getsongbpm_bpm)}")

if __name__ == "__main__":
    test_bpm_analysis()
