"""
Interactive Tempo Craft - Spotify BPM Playlist Creator
Enhanced version with playlist creation ca        # Show analysis summary
    bpm_tracks = [t for t in analyzed_tracks if t.bpm is not None]
    spotify_bpm = [t for t in bpm_tracks if t.bpm_source == "spotify"]
    acousticbrainz_bpm = [t for t in bpm_tracks if t.bpm_source == "acousticbrainz"]
    getsongbpm_bpm = [t for t in bpm_tracks if t.bpm_source == "getsongbpm"]w analysis summary
    bpm_tracks = [t for t in analyzed_tracks if t.bpm is not None]
    spotify_bpm = [t for t in bpm_tracks if t.bpm_source == "spotify"]
    acousticbrainz_bpm = [t for t in bpm_tracks if t.bmp_source == "acousticbrainz"]
    getsongbpm_bpm = [t for t in bpm_tracks if t.bpm_source == "getsongbpm"]ities
"""
from typing import List, Optional
from config import Config
from src.auth.spotify_auth import SpotifyAuth
from src.models.track import Track
from src.analyzer.music_analyzer import MusicAnalyzer
from src.analyzer.acousticbrainz_analyzer import AcousticBrainzAnalyzer
from src.analyzer.getsongbpm_analyzer import GetSongBPMAnalyzer
from src.playlist.playlist_manager import PlaylistManager
from user_interface import UserInterface
from src.exceptions.exception_handler import ExceptionHandler
from src.exceptions.track_exceptions import TrackParsingError, TrackValidationError
from src.exceptions.spotify_exceptions import SpotifyConnectionError, SpotifyAuthenticationError
from src.exceptions.analysis_exceptions import ExternalAPIError

def main() -> None:
    # Display welcome
    UserInterface.display_welcome()
    
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
    
    # Step 2: Setup analyzers and playlist manager
    print("\n🔧 Setting up analyzers...")
    sp = auth.get_client()
    
    if not sp:
        print("❌ Spotify client not available")
        return

    # Create analyzers (re-enable GetSongBPM with corrected API)
    acousticbrainz_analyzer = AcousticBrainzAnalyzer()
    getsongbpm_analyzer = GetSongBPMAnalyzer(config.getsongbpm_api_key)
    analyzer = MusicAnalyzer(sp, acousticbrainz_analyzer, getsongbpm_analyzer)
    
    # Create playlist manager
    playlist_manager = PlaylistManager(sp)

    # Show fallback status
    fallback_status = analyzer.get_fallback_status()
    print(f"📡 Fallback status:")
    print(f"   AcousticBrainz: {'✅ available' if fallback_status['acousticbrainz_available'] else '❌ unavailable'}")
    print(f"   GetSongBPM: {'✅ available' if fallback_status['getsongbpm_available'] else '❌ unavailable'}")

    # Step 3: Get user's top tracks (limited to 10 for testing)
    print("\n🎵 Getting your top tracks...")
    try:
        top_tracks_response = sp.current_user_top_tracks(limit=10, time_range='medium_term')
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
    
    # Step 5: Analyze tracks
    print(f"\n🔍 Analyzing {len(tracks)} tracks...")
    analyzed_tracks = analyzer.analyze_tracks(tracks)
    
    # Show analysis summary
    bpm_tracks = [t for t in analyzed_tracks if t.bpm is not None]
    spotify_bpm = [t for t in bpm_tracks if t.bpm_source == "spotify"]
    acousticbrainz_bpm = [t for t in bpm_tracks if t.bpm_source == "acousticbrainz"]
    getsongbpm_bpm = [t for t in bpm_tracks if t.bpm_source == "getsongbpm"]
    
    print(f"\n📊 Analysis Complete!")
    print(f"   Total tracks analyzed: {len(analyzed_tracks)}")
    print(f"   Tracks with BPM: {len(bpm_tracks)}")
    print(f"   From Spotify: {len(spotify_bpm)}")
    print(f"   From AcousticBrainz: {len(acousticbrainz_bpm)}")
    print(f"   From GetSongBPM: {len(getsongbpm_bpm)}")
    
    if len(bpm_tracks) == 0:
        print("\n❌ No tracks with BPM data found. Cannot create playlist.")
        return
    
    # Step 6: Get user filtering preferences
    genre_keyword, min_bpm, max_bpm = UserInterface.get_user_filters()
    
    # Step 7: Create playlist
    print(f"\n🎵 Creating playlist...")
    print(f"   Genre filter: {genre_keyword}")
    print(f"   BPM range: {min_bpm} - {max_bpm}")
    
    try:
        playlist_id = playlist_manager.create_bpm_playlist(
            analyzed_tracks, min_bpm, max_bpm, genre_keyword
        )
        
        if playlist_id:
            playlist_url = playlist_manager.get_playlist_url(playlist_id)
            
            # Get final track count
            filtered_tracks = playlist_manager.filter_tracks_combined(
                analyzed_tracks, min_bpm, max_bpm, genre_keyword
            )
            
            # Display success
            playlist_name = f"Tempo Craft {int(min_bpm)}-{int(max_bpm)} BPM"
            if genre_keyword:
                playlist_name += f" - {genre_keyword.title()}"
            
            UserInterface.display_summary(
                len(analyzed_tracks), 
                len(filtered_tracks),
                playlist_name
            )
            
            print(f"\n🔗 Playlist URL: {playlist_url}")
            
        else:
            print("\n❌ No tracks match your criteria. Try adjusting your filters.")
            
    except Exception as e:
        print(f"\n❌ Failed to create playlist: {e}")

if __name__ == "__main__":
    main()
