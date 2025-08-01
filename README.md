# 🎵 Tempo Craft - Spotify BPM Playlist Creator

A modular Python application that analyzes your Spotify tracks for BPM (tempo) and genres, with multiple fallback APIs for comprehensive music analysis.

## ✨ Features

- **Spotify Integration**: Fetch your top tracks directly from Spotify
- **Multi-Source BPM Analysis**: 
  - Primary: Spotify Audio Features API
  - Fallback 1: AcousticBrainz API
  - Fallback 2: GetSongBPM.com API
- **Genre Detection**: Automatic genre extraction from Spotify artist data
- **Robust Error Handling**: Graceful handling of API failures and rate limits
- **Modular Architecture**: Clean separation of concerns with custom exception handling

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Spotify Developer Account
- Optional: GetSongBPM.com API key for enhanced BPM coverage

### Installation

1. Clone the repository:
```bash
git clone https://github.com/oguzhanyetimoglu/tempo-craft.git
cd tempo-craft
```

2. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your Spotify API credentials
```

### Configuration

Create a `.env` file with your API credentials:

```env
# Spotify API Credentials (Required)
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
SPOTIFY_REDIRECT_URI=http://127.0.0.1:8888/callback

# GetSongBPM API Key (Optional - for enhanced BPM coverage)
GETSONGBPM_API_KEY=your_getsongbpm_api_key
```

### Usage

Run the main application:
```bash
python main.py
```

The application will:
1. Connect to your Spotify account
2. Fetch your top tracks
3. Analyze each track for BPM and genres
4. Display comprehensive results with source attribution

## 🏗️ Architecture

### Project Structure
```
tempo-craft/
├── src/
│   ├── auth/           # Spotify authentication
│   ├── models/         # Data models (Track)
│   ├── analyzer/       # Music analysis engines
│   └── exceptions/     # Custom exception handling
├── main.py            # Application entry point
├── config.py          # Configuration management
└── requirements.txt   # Python dependencies
```

### Analysis Pipeline

1. **Authentication**: Secure OAuth2 flow with Spotify
2. **Data Fetching**: Retrieve user's top tracks
3. **Track Parsing**: Validate and structure track data
4. **BPM Analysis**: Multi-source fallback system
5. **Genre Analysis**: Extract artist genres from Spotify
6. **Results Display**: Comprehensive track information

## 🔧 API Integration

### Spotify Web API
- **Purpose**: Primary data source for tracks and audio features
- **Features**: Track metadata, audio features, artist genres
- **Authentication**: OAuth2 with PKCE flow

### AcousticBrainz API
- **Purpose**: Primary BPM fallback source
- **Features**: Detailed audio analysis via MusicBrainz integration
- **Authentication**: No API key required

### GetSongBPM.com API
- **Purpose**: Secondary BPM fallback source
- **Features**: Large commercial music database
- **Authentication**: API key required (free tier available)

## 📊 Example Output

```
🎵 Tempo Craft - Spotify BPM Playlist Creator
🎵 Connecting to Spotify...
✅ Connected successfully: Your Name

🔧 Setting up analyzers...
📡 Fallback status:
   AcousticBrainz: ✅ available
   GetSongBPM: ✅ available

🎵 Getting your top tracks...
📝 Parsing 10 tracks...
🔍 Analyzing 10 tracks...

📊 Analysis Results:

1. Artist - Track Name
   ID: spotify_track_id
   Popularity: 85
   BPM: 128.0 (from acousticbrainz)
   Genres: electronic, house, dance

📈 BPM Analysis Summary:
   Total tracks with BPM: 8
   From Spotify: 3
   From AcousticBrainz: 4
   From GetSongBPM: 1
```

## � Testing

### Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_unit.py -v

# Run with coverage
python -m pytest tests/ --cov=src/

# Quick BPM analysis test
python tests/test_bpm_analysis.py
```

### Test Structure

```
tests/
├── __init__.py
├── test_unit.py              # Unit tests for models and utilities
├── test_bpm_analysis.py      # BPM analysis integration tests
└── test_playlist_creation.py # Playlist creation tests
```

## 🔧 Development

### Type Checking

```bash
# Run mypy type checking
python -m mypy src/ --ignore-missing-imports
```

### Code Quality

- **Type Hints**: Comprehensive type annotations using Python typing
- **Error Handling**: Custom exception classes for different failure modes  
- **Modular Design**: Clean separation between analysis, auth, and playlist logic
- **Logging**: Detailed logging for debugging and monitoring

## �🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Credits

- **Music Data**: [Spotify Web API](https://developer.spotify.com/documentation/web-api/)
- **BPM Analysis**: [AcousticBrainz](https://acousticbrainz.org/) & [GetSongBPM.com](https://getsongbpm.com)
- **Music Metadata**: [MusicBrainz](https://musicbrainz.org/)

## 📞 Support

If you encounter any issues or have questions, please open an issue on GitHub.

---

Made with ❤️ for music enthusiasts and data lovers
