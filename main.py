"""
Tempo Craft - Spotify BPM Playlist Creator
Simple main entry point with AcousticBrainz fallback support
"""
from config import Config
from src.auth.spotify_auth import SpotifyAuth
from src.models.track import Track
from src.analyzer.music_analyzer import MusicAnalyzer
from src.analyzer.acousticbrainz_analyzer import AcousticBrainzAnalyzer
from src.analyzer.getsongbpm_analyzer import GetSongBPMAnalyzer
from src.exceptions.exception_handler import ExceptionHandler
from src.exceptions.track_exceptions import TrackParsingError, TrackValidationError
from src.exceptions.spotify_exceptions import SpotifyConnectionError, SpotifyAuthenticationError
from src.exceptions.analysis_exceptions import ExternalAPIError

def main():
    print("🎵 Tempo Craft - Spotify BPM Playlist Creator")
    
    # Initialize configuration
    config = Config()
    
    # Step 1: Connect to Spotify
    try:
        auth = SpotifyAuth()
        auth.connect()
    except SpotifyAuthenticationError as e:
        print(f"❌ Authentication failed: {e}")
        return
    except SpotifyConnectionError as e:
        print(f"❌ Connection failed: {e}")
        return
    
    # Step 2: Setup analyzers
    print("\n🔧 Setting up analyzers...")
    sp = auth.get_client()
    
    if not sp:
        print("❌ Spotify client not available")
        return

    # Create main analyzer with AcousticBrainz and GetSongBPM fallbacks
    acousticbrainz_analyzer = AcousticBrainzAnalyzer()
    getsongbpm_analyzer = GetSongBPMAnalyzer(config.getsongbpm_api_key)
    analyzer = MusicAnalyzer(sp, acousticbrainz_analyzer, getsongbpm_analyzer)

    # Show fallback status
    fallback_status = analyzer.get_fallback_status()
    print(f"📡 Fallback status:")
    print(f"   AcousticBrainz: {'✅ available' if fallback_status['acousticbrainz_available'] else '❌ unavailable'}")
    print(f"   GetSongBPM: {'✅ available' if fallback_status['getsongbpm_available'] else '❌ unavailable'}")

    # Step 3: Get user's top tracks
    print("\n🎵 Getting your top tracks...")
    try:
        top_tracks_response = sp.current_user_top_tracks(limit=10)  # Maximum allowed by Spotify
        if not top_tracks_response or 'items' not in top_tracks_response:
            print("❌ No tracks found")
            return
        
        top_tracks = top_tracks_response['items']
    except Exception as e:
        print(ExceptionHandler.handle_spotify_connection(e))
        return
    
    # Step 4: Parse tracks
    print(f"\n📝 Parsing {len(top_tracks)} tracks...")
    tracks = []
    for i, spotify_track in enumerate(top_tracks, 1):
        try:
            # Check if required fields exist
            required_fields = ['id', 'name', 'uri', 'popularity', 'artists']
            if not all(key in spotify_track for key in required_fields):
                missing = [key for key in required_fields if key not in spotify_track]
                raise TrackParsingError(f"Missing required fields: {missing}")
            
            if not spotify_track['artists'] or 'name' not in spotify_track['artists'][0]:
                raise TrackParsingError("Missing artist information")
            
            track = Track(
                id=spotify_track['id'],
                name=spotify_track['name'],
                artist=spotify_track['artists'][0]['name'],
                uri=spotify_track['uri'],
                popularity=spotify_track['popularity']
            )
            tracks.append(track)
            
        except (TrackParsingError, TrackValidationError) as e:
            print(f"⚠️ Skipping track {i}: {e}")
            continue
    
    # Step 5: Analyze tracks with enhanced error handling
    print(f"\n🔍 Analyzing {len(tracks)} tracks...")
    analyzed_tracks = analyzer.analyze_tracks(tracks)
    
    # Step 6: Display results
    print("\n📊 Analysis Results:")
    for i, track in enumerate(analyzed_tracks, 1):
        print(f"\n{i}. {track}")
        print(f"   ID: {track.id}")
        print(f"   Popularity: {track.popularity}")
        print(f"   BPM: {track.bpm}" + (f" (from {track.bpm_source})" if track.bpm_source else ""))
        print(f"   Genres: {', '.join(track.genres) if track.genres else 'None'}")
    
    print(f"\n✅ Successfully analyzed {len(analyzed_tracks)} out of {len(tracks)} tracks!")
    
    # Show summary
    bpm_tracks = [t for t in analyzed_tracks if t.bpm is not None]
    spotify_bpm = [t for t in bpm_tracks if t.bpm_source == "spotify"]
    acousticbrainz_bpm = [t for t in bpm_tracks if t.bpm_source == "acousticbrainz"]
    
    print(f"\n📈 BPM Analysis Summary:")
    print(f"   Total tracks with BPM: {len(bpm_tracks)}")
    print(f"   From Spotify: {len(spotify_bpm)}")
    print(f"   From AcousticBrainz: {len(acousticbrainz_bpm)}")

if __name__ == "__main__":
    main()
