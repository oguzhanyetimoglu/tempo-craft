"""
User interface and input handling
"""
from typing import Tuple, Optional

class UserInterface:
    @staticmethod
    def get_user_filters() -> Tuple[str, float, float]:
        """Get filtering criteria from user"""
        print("\n🎛️ Filter Settings")
        print("-" * 30)
        
        while True:
            try:
                genre_keyword = input("Desired genre (example: rock, pop, techno): ").lower().strip()
                if genre_keyword:
                    break
                print("Please enter a genre keyword.")
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                exit(0)
        
        while True:
            try:
                min_bpm = float(input("Minimum BPM: "))
                if min_bpm > 0:
                    break
                print("Please enter a positive number.")
            except ValueError:
                print("Please enter a valid number.")
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                exit(0)
        
        while True:
            try:
                max_bpm = float(input("Maximum BPM: "))
                if max_bpm > min_bpm:
                    break
                print(f"Maximum BPM must be greater than {min_bpm}.")
            except ValueError:
                print("Please enter a valid number.")
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                exit(0)
        
        return genre_keyword, min_bpm, max_bpm
    
    @staticmethod
    def display_welcome():
        """Display welcome message"""
        print("🎵" + "=" * 50 + "🎵")
        print("     TEMPO CRAFT - Spotify Playlist Creator")
        print("🎵" + "=" * 50 + "🎵")
        print("Create personalized playlists based on BPM and genre!")
        print()
    
    @staticmethod
    def display_summary(total_tracks: int, filtered_tracks: int, playlist_name: str):
        """Display operation summary"""
        print("\n📊 Summary")
        print("-" * 30)
        print(f"📀 Total tracks analyzed: {total_tracks}")
        print(f"✅ Tracks matching criteria: {filtered_tracks}")
        print(f"🎵 Playlist created: {playlist_name}")
        print("\n🎉 Done! Check your Spotify app for the new playlist.")
    
    @staticmethod
    def confirm_action(message: str) -> bool:
        """Get user confirmation"""
        while True:
            try:
                response = input(f"{message} (y/n): ").lower().strip()
                if response in ['y', 'yes']:
                    return True
                elif response in ['n', 'no']:
                    return False
                else:
                    print("Please enter 'y' or 'n'.")
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                exit(0)
