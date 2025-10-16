"""
Main Telegram Bot for Mezmur
"""
import os
import asyncio
import logging
from dotenv import load_dotenv
from telegram import Update, BotCommand, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, InlineQueryHandler, filters, ContextTypes
from utils.api_client import MezmurAPIClient
from handlers.search import SearchHandler
from handlers.lyrics import LyricsHandler
from handlers.albums import AlbumsHandler

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Bot configuration
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000')

if not BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")


class MezmurBot:
    """Main Mezmur Telegram Bot"""
    
    def __init__(self, bot_token: str, api_base_url: str):
        self.bot_token = bot_token
        self.api_base_url = api_base_url
        
        # Initialize API client
        self.api_client = MezmurAPIClient(api_base_url)
        
        # Initialize handlers
        self.search_handler = SearchHandler(self.api_client)
        self.lyrics_handler = LyricsHandler(self.api_client)
        self.albums_handler = AlbumsHandler(self.api_client)
        
        # Initialize application
        self.application = Application.builder().token(bot_token).build()
        
        # Register handlers
        self._register_handlers()
    
    def _register_handlers(self):
        """Register all command and message handlers"""
        
        # Start and help commands
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        
        # Search commands
        self.application.add_handler(CommandHandler("search", self.search_handler.search_command))
        self.application.add_handler(CommandHandler("search_full", self.search_handler.search_full_command))
        
        # Lyrics commands
        self.application.add_handler(CommandHandler("lyrics", self.lyrics_handler.lyrics_command))
        self.application.add_handler(CommandHandler("rich_lyrics", self.lyrics_handler.rich_lyrics_command))
        self.application.add_handler(CommandHandler("random_lyrics", self.lyrics_handler.random_lyrics_command))
        
        # Albums and artists commands
        self.application.add_handler(CommandHandler("artist", self.albums_handler.artist_command))
        self.application.add_handler(CommandHandler("album", self.albums_handler.album_command))
        self.application.add_handler(CommandHandler("artists", self.albums_handler.artists_command))
        
        # Callback query handlers
        self.application.add_handler(CallbackQueryHandler(self.search_handler.handle_callback_query))
        self.application.add_handler(CallbackQueryHandler(self.albums_handler.handle_callback_query))
        
        # Inline query handler
        self.application.add_handler(InlineQueryHandler(self.handle_inline_query))
        
        # Message handlers
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text_message))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        if not update.effective_message:
            return
        welcome_message = """
🎵 **Welcome to Mezmur Bot!** 🎵

I can help you find and listen to Ethiopian music lyrics. Here's what I can do:

🔍 **Search Commands:**
• `/search <query>` - Fast search for titles starting with your query
• `/search_full <query>` - Broader search that looks anywhere in content

🎵 **Lyrics Commands:**
• `/lyrics <song_title>` - Get plain text lyrics
• `/rich_lyrics <song_title>` - Get lyrics with HTML formatting
• `/random_lyrics` - Get random lyrics

👤 **Artist & Album Commands:**
• `/artist <artist_name>` - Get albums by an artist
• `/album <album_title>` - Get songs in an album
• `/artists` - List all available artists

📖 **Help:**
• `/help` - Show this help message

**Examples:**
• `/search samuel tesfa`
• `/artist Samuel Tesfamichael`
• `/lyrics Samuel Tesfamichael/Misale Yeleleh/Yekebere`

Just type any of these commands to get started! 🚀
        """
        
        await update.effective_message.reply_text(welcome_message, parse_mode='Markdown')
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        if not update.effective_message:
            return
        help_message = """
📖 **Mezmur Bot Help** 📖

**Search Commands:**
🔍 `/search <query>` - Fast prefix search
🔍 `/search_full <query>` - Full text search

**Lyrics Commands:**
🎵 `/lyrics <song_title>` - Plain text lyrics
🎵 `/rich_lyrics <song_title>` - HTML formatted lyrics
🎵 `/random_lyrics` - Random song lyrics

**Artist & Album Commands:**
👤 `/artist <artist_name>` - Artist's albums
💿 `/album <album_title>` - Album's songs
👥 `/artists` - List all artists

**Song Title Format:**
`Artist/Album/Song`
Example: `Samuel Tesfamichael/Misale Yeleleh/Yekebere`

**Need Help?**
Contact @your_username for support
        """
        
        await update.effective_message.reply_text(help_message, parse_mode='Markdown')
    
    async def handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular text messages (non-commands)"""
        if not update.effective_message:
            return
            
        message_text = (update.effective_message.text or "").lower()
        
        # Simple keyword detection for common searches
        if any(keyword in message_text for keyword in ['samuel', 'tesfamichael', 'misale', 'yeleleh']):
            await update.effective_message.reply_text(
                "🔍 I detected you might be looking for music!\n\n"
                "Try these commands:\n"
                "• `/search samuel tesfa` - Search for Samuel Tesfamichael\n"
                "• `/search misale` - Search for Misale Yeleleh\n"
                "• `/artist Samuel Tesfamichael` - Get his albums\n\n"
                "Type `/help` for more commands!",
                parse_mode='Markdown'
            )
        else:
            await update.effective_message.reply_text(
                "👋 Hi! I'm Mezmur Bot, your Ethiopian music assistant.\n\n"
                "Type `/start` to see what I can do, or `/help` for command help!",
                parse_mode='Markdown'
            )
    
    async def handle_inline_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle inline queries for instant search - songs only with lyrics and pagination"""
        if not update.inline_query:
            return
            
        query = update.inline_query.query
        offset = int(update.inline_query.offset or 0)  # Get current offset for pagination
        
        if not query or len(query) < 2:
            return
        
        try:
            logger.info(f"Processing inline query: '{query}' with offset: {offset}")
            
            # Check if we have cached results for this query
            cache_key = f"search_{query}"
            if not hasattr(self, '_search_cache'):
                self._search_cache = {}
            
            # If offset is 0, perform new search and cache results
            if offset == 0 or cache_key not in self._search_cache:
                logger.info(f"Performing new search for query: '{query}'")
                # Perform search with higher limit to get more results for pagination
                results = await self.api_client.search_prefix(query, limit=50)
                logger.info(f"Search returned {len(results.data)} results")
                
                if not results.data:
                    return
                
                # Filter only songs (more than 1 slash = song)
                songs = [result for result in results.data if result.title.count("/") > 1]
                logger.info(f"Found {len(songs)} songs after filtering")
                
                if not songs:
                    logger.info("No songs found, returning empty results")
                    return
                
                # Cache the songs list
                self._search_cache[cache_key] = songs
                logger.info(f"Cached {len(songs)} songs for query: '{query}'")
            else:
                # Use cached results
                songs = self._search_cache[cache_key]
                logger.info(f"Using cached results: {len(songs)} songs for query: '{query}'")
            
            # Calculate pagination
            songs_per_page = 5
            start_idx = offset
            end_idx = start_idx + songs_per_page
            songs_to_show = songs[start_idx:end_idx]
            
            # Create inline results for current page
            inline_results = []
            for i, song in enumerate(songs_to_show):
                song_name = song.title.split("/")[-1]
                artist_name = song.title.split("/")[0]
                
                try:
                    # Fetch the actual lyrics for this song
                    logger.info(f"Fetching lyrics for song: {song.title}")
                    lyrics_data = await self.api_client.get_lyrics(song.title)
                    logger.info(f"Lyrics data received: {lyrics_data}")
                    
                    # Create the lyrics message
                    lyrics_text = lyrics_data.get("lyrics", "No lyrics available")
                    title = lyrics_data.get("title", song_name)
                    artist = lyrics_data.get("artist", artist_name)
                    album = lyrics_data.get("album", "")
                    
                    # Format the message
                    message = f"🎵 **{title}**\n"
                    if artist:
                        message += f"👤 by {artist}\n"
                    if album:
                        message += f"💿 from {album}\n"
                    message += "\n" + "="*30 + "\n\n"
                    message += lyrics_text
                    
                    # Truncate if too long (Telegram has message limits)
                    if len(message) > 4000:
                        message = message[:3900] + "\n\n... (truncated)"
                    
                    logger.info(f"Created message for {song_name}: {message[:200]}...")
                    
                    # Create inline result with actual lyrics
                    inline_result = InlineQueryResultArticle(
                        id=f"{offset}_{i}",
                        title=f"🎵 {song_name}",
                        description=f"by {artist_name}",
                        input_message_content=InputTextMessageContent(
                            message_text=message,
                            parse_mode='Markdown'
                        )
                    )
                    inline_results.append(inline_result)
                    
                except Exception as lyrics_error:
                    logger.error(f"Failed to fetch lyrics for {song.title}: {lyrics_error}")
                    logger.error(f"Error type: {type(lyrics_error).__name__}")
                    
                    # Try to get more details about the error if it's an HTTP error
                    import httpx
                    if isinstance(lyrics_error, httpx.HTTPStatusError):
                        logger.error(f"HTTP Status: {lyrics_error.response.status_code}")
                        logger.error(f"Response text: {lyrics_error.response.text}")
                    
                    # Fallback to showing command if lyrics fetch fails
                    inline_result = InlineQueryResultArticle(
                        id=f"{offset}_{i}",
                        title=f"🎵 {song_name}",
                        description=f"by {artist_name}",
                        input_message_content=InputTextMessageContent(
                            message_text=f"🎵 **{song_name}**\n"
                                       f"👤 by {artist_name}\n\n"
                                       f"❌ Lyrics temporarily unavailable\n"
                                       f"Use `/lyrics {song.title}` to try again!",
                            parse_mode='Markdown'
                        )
                    )
                    inline_results.append(inline_result)
            
            # Add loading indicator only on first page to show there are more results
            # On subsequent pages, we don't show loading indicator so users can see fresh content
            if end_idx < len(songs) and offset == 0:
                remaining_songs = len(songs) - end_idx
                loading_result = InlineQueryResultArticle(
                    id=f"loading_{offset}",
                    title="⏳ Load More Songs",
                    description=f"{remaining_songs} more songs available - scroll down",
                    input_message_content=InputTextMessageContent(
                        message_text=f"⏳ **Load More Songs**\n\n"
                                   f"📊 {remaining_songs} more songs available\n"
                                   f"🔄 Scroll down to load more results",
                        parse_mode='Markdown'
                    )
                )
                inline_results.append(loading_result)
                logger.info(f"Added loading indicator: {remaining_songs} more songs available")
            elif end_idx < len(songs) and offset > 0:
                # On subsequent pages, just log that there are more songs but don't show indicator
                remaining_songs = len(songs) - end_idx
                logger.info(f"Page {offset//5 + 1}: {remaining_songs} more songs available (no loading indicator shown)")
            
            # Calculate next offset for pagination
            next_offset = str(end_idx) if end_idx < len(songs) else None
            
            # Answer the inline query with pagination support
            logger.info(f"Returning {len(inline_results)} inline results, next_offset: {next_offset}")
            await update.inline_query.answer(
                inline_results, 
                cache_time=300,
                next_offset=next_offset
            )
            
        except Exception as e:
            logger.error(f"Inline query failed: {e}")
    
    async def health_check(self):
        """Check if the API is healthy"""
        try:
            health = await self.api_client.health_check()
            logger.info(f"API health check: {health}")
            return True
        except Exception as e:
            logger.error(f"API health check failed: {e}")
            return False
    
    async def _set_bot_commands(self):
        """Set bot commands menu"""
        try:
            commands = [
                BotCommand("start", "Start the bot and see welcome message"),
                BotCommand("help", "Show help and available commands"),
                BotCommand("search", "Search for music (prefix search)"),
                BotCommand("search_full", "Full text search for music"),
                BotCommand("lyrics", "Get plain text lyrics for a song"),
                BotCommand("rich_lyrics", "Get HTML formatted lyrics"),
                BotCommand("random_lyrics", "Get random song lyrics"),
                BotCommand("artist", "Get albums by an artist"),
                BotCommand("album", "Get songs in an album"),
                BotCommand("artists", "List all available artists"),
            ]
            await self.application.bot.set_my_commands(commands)
            logger.info("Bot commands menu set successfully")
        except Exception as e:
            logger.error(f"Failed to set bot commands: {e}")
    
    async def start_bot(self):
        """Start the bot"""
        logger.info("Starting Mezmur Bot...")
        
        # Check API health
        if not await self.health_check():
            logger.error("API is not healthy. Please check the API service.")
            return
        
        # Start the bot
        await self.application.initialize()
        await self.application.start()
        
        # Set bot commands menu
        await self._set_bot_commands()
        
        if self.application.updater:
            await self.application.updater.start_polling()
        
        logger.info("Mezmur Bot started successfully!")
        
        # Keep the bot running
        try:
            await asyncio.Event().wait()
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
        finally:
            await self.stop_bot()
    
    async def stop_bot(self):
        """Stop the bot"""
        logger.info("Stopping Mezmur Bot...")
        
        if self.application.updater:
            await self.application.updater.stop()
        await self.application.stop()
        await self.application.shutdown()
        
        # Close API client
        await self.api_client.close()
        
        logger.info("Mezmur Bot stopped.")


async def main():
    """Main function to run the bot"""
    try:
        # Create and start the bot
        bot = MezmurBot(BOT_TOKEN, API_BASE_URL)  # type: ignore
        await bot.start_bot()
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        raise


if __name__ == '__main__':
    # Run the bot
    asyncio.run(main())
