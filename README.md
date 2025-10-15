# Mezmur Telegram Bot

A Telegram bot for discovering and listening to Ethiopian music lyrics, powered by the Mezmur FastAPI service.

## Features

- 🔍 **Search**: Fast prefix search and full text search
- 🎵 **Lyrics**: Get plain text or rich HTML formatted lyrics
- 👤 **Artists**: Browse artists and their albums
- 💿 **Albums**: Explore albums and their songs
- 🎯 **Interactive**: Clickable buttons for easy navigation

## Commands

### Search Commands

- `/search <query>` - Fast prefix search
- `/search_full <query>` - Full text search

### Lyrics Commands

- `/lyrics <song_title>` - Plain text lyrics
- `/rich_lyrics <song_title>` - HTML formatted lyrics
- `/random_lyrics` - Random song lyrics

### Artist & Album Commands

- `/artist <artist_name>` - Get albums by artist
- `/album <album_title>` - Get songs in album
- `/artists` - List all artists

## Setup

### 1. Prerequisites

- Python 3.11+
- Telegram Bot Token (from @BotFather)
- Running Mezmur API service

### 2. Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd telegram-bot

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export TELEGRAM_BOT_TOKEN="your_bot_token_here"
export API_BASE_URL="http://localhost:8000"
```

### 3. Running the Bot

```bash
# Start the bot
python bot.py
```

### 4. Using Docker

```bash
# Build and run with Docker Compose
docker-compose up --build
```

## Configuration

### Environment Variables

- `TELEGRAM_BOT_TOKEN` - Your Telegram bot token (required)
- `API_BASE_URL` - URL of the Mezmur API service (default: http://localhost:8000)

### Getting a Telegram Bot Token

1. Message @BotFather on Telegram
2. Use `/newbot` command
3. Follow the instructions to create your bot
4. Copy the token and set it as `TELEGRAM_BOT_TOKEN`

## Usage Examples

### Search for Music

```
/search samuel tesfa
/search_full misale
```

### Get Lyrics

```
/lyrics Samuel Tesfamichael/Misale Yeleleh/Yekebere
/rich_lyrics Samuel Tesfamichael/Misale Yeleleh/Yekebere
```

### Browse Artists and Albums

```
/artist Samuel Tesfamichael
/album Samuel Tesfamichael/Misale Yeleleh
/artists
```

## Architecture

```
telegram-bot/
├── bot.py                 # Main bot application
├── handlers/              # Command handlers
│   ├── search.py         # Search functionality
│   ├── lyrics.py         # Lyrics functionality
│   └── albums.py         # Albums and artists
├── utils/
│   └── api_client.py     # API client for Mezmur service
└── requirements.txt      # Python dependencies
```

## Development

### Adding New Commands

1. Create a new handler in `handlers/`
2. Add the command to `bot.py`
3. Register the handler in `_register_handlers()`

### API Client

The bot communicates with the Mezmur API through the `MezmurAPIClient` class in `utils/api_client.py`. This client handles all HTTP requests and response parsing.

## Deployment

### Docker Deployment

```bash
# Build and run
docker-compose up --build

# Run in background
docker-compose up -d
```

### Manual Deployment

1. Set up a server (Ubuntu, CentOS, etc.)
2. Install Python 3.11+
3. Clone the repository
4. Install dependencies
5. Set environment variables
6. Run the bot as a service

### Production Considerations

- Use a process manager like systemd or supervisor
- Set up logging and monitoring
- Configure proper error handling
- Use environment variables for configuration
- Consider using a reverse proxy (nginx)

## Troubleshooting

### Common Issues

1. **Bot not responding**: Check if the API service is running
2. **API errors**: Verify the API_BASE_URL is correct
3. **Token errors**: Ensure TELEGRAM_BOT_TOKEN is set correctly

### Logs

The bot logs all activities. Check the console output for error messages.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.
