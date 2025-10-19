# """
# Main Telegram Bot for Mezmur - Refactored with Services Architecture
# """
# import os
# import asyncio
# import logging
# from dotenv import load_dotenv
# from telegram import Update, BotCommand, InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardButton, InlineKeyboardMarkup
# from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, InlineQueryHandler, filters, ContextTypes
# from utils.api_client import MezmurAPIClient
# from services.mediator import CallbackMediator
# from handlers_new.search_commands import SearchCommands
# from handlers_new.lyrics_commands import LyricsCommands
# from handlers_new.album_commands import AlbumCommands

# # Configure logging
# logging.basicConfig(
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     level=logging.DEBUG
# )
# logger = logging.getLogger(__name__)

# # Load environment variables from .env file
# load_dotenv()

# # Bot configuration
# BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
# API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000')

# if not BOT_TOKEN:
#     raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")


# class MezmurBot:
#     """Main Mezmur Telegram Bot - Refactored Architecture"""
    
#     def __init__(self, bot_token: str, api_base_url: str):
#         self.bot_token = bot_token
#         self.api_base_url = api_base_url
        
#         # Initialize API client
#         self.api_client = MezmurAPIClient(api_base_url)
        
#         # Initialize mediator for callback routing
#         self.mediator = CallbackMediator(self.api_client)
        
#         # Initialize command handlers (thin wrappers)
#         self.search_commands = SearchCommands(self.api_client, self.mediator)
#         self.lyrics_commands = LyricsCommands(self.api_client)
#         self.album_commands = AlbumCommands(self.api_client)
        
#         # Initialize application
#         self.application = Application.builder().token(bot_token).build()
        
#         # User conversation states - tracks what each user is waiting for
#         self.user_states = {}
        
#         # Register handlers
#         self._register_handlers()
    
#     def _register_handlers(self):
#         """Register all command and message handlers"""
        
#         # Start and help commands
#         self.application.add_handler(CommandHandler("start", self.start_command))
#         self.application.add_handler(CommandHandler("help", self.help_command))
        
#         # Search commands
#         self.application.add_handler(CommandHandler("search", self.search_commands.search_command))
#         self.application.add_handler(CommandHandler("search_full", self.search_commands.search_full_command))
        
#         # Lyrics commands
#         self.application.add_handler(CommandHandler("lyrics", self.lyrics_commands.lyrics_command))
#         self.application.add_handler(CommandHandler("rich_lyrics", self.lyrics_commands.rich_lyrics_command))
#         self.application.add_handler(CommandHandler("random_lyrics", self.lyrics_commands.random_lyrics_command))
        
#         # Albums and artists commands
#         self.application.add_handler(CommandHandler("artist", self.album_commands.artist_command))
#         self.application.add_handler(CommandHandler("album", self.album_commands.album_command))
#         self.application.add_handler(CommandHandler("artists", self.album_commands.artists_command))
        
#         # Callback query handler - all callbacks go through the mediator
#         self.application.add_handler(CallbackQueryHandler(self.mediator.handle_callback))
        
#         # Inline query handler
#         self.application.add_handler(InlineQueryHandler(self.handle_inline_query))
        
#         # Message handlers
#         self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text_message))
    
#     async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
#         """Handle /start command"""
#         if not update.effective_message:
#             return
        
#         welcome_message = """
# 🎵 **Welcome to Mezmur Bot!** 🎵

# I can help you find and listen to Ethiopian music lyrics. Choose what you'd like to do:

# **Quick Actions:**
# Use the buttons below to get started quickly!

# **Commands:**
# • `/search <query>` - Fast prefix search
# • `/search_full <query>` - Broader search
# • `/lyrics <song>` - Get song lyrics
# • `/artist <name>` - Find albums by artist
# • `/album <title>` - Find songs in album
# • `/artists` - List all artists
# • `/random_lyrics` - Get random lyrics

# **Examples:**
# • `/search samuel tesfa`
# • `/lyrics Samuel Tesfamichael/Misale Yeleleh/Yekebere`
# • `/artist Samuel Tesfamichael`

# Type `/help` for more information!
#         """
        
#         # Create welcome keyboard
#         keyboard = [
#             [
#                 InlineKeyboardButton("🔍 Search", callback_data="search_artist"),
#                 InlineKeyboardButton("🎵 Random Lyrics", callback_data="random_lyrics")
#             ],
#             [
#                 InlineKeyboardButton("👤 Browse Artists", callback_data="search_artist"),
#                 InlineKeyboardButton("💿 Browse Albums", callback_data="search_album")
#             ]
#         ]
#         reply_markup = InlineKeyboardMarkup(keyboard)
        
#         await update.effective_message.reply_text(
#             welcome_message,
#             parse_mode='Markdown',
#             reply_markup=reply_markup
#         )
    
#     async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
#         """Handle /help command"""
#         if not update.effective_message:
#             return
        
#         help_message = """
# 🎵 **Mezmur Bot Help** 🎵

# **Search Commands:**
# • `/search <query>` - Fast prefix search for titles starting with your query
# • `/search_full <query>` - Broader search that looks anywhere in content

# **Lyrics Commands:**
# • `/lyrics <song_title>` - Get plain text lyrics
# • `/rich_lyrics <song_title>` - Get lyrics with HTML formatting
# • `/random_lyrics` - Get random song lyrics

# **Browse Commands:**
# • `/artist <artist_name>` - Get all albums by artist
# • `/album <album_title>` - Get all songs in album
# • `/artists` - List all available artists

# **Examples:**
# • `/search samuel tesfa`
# • `/lyrics Samuel Tesfamichael/Misale Yeleleh/Yekebere`
# • `/artist Samuel Tesfamichael`
# • `/album Samuel Tesfamichael/Misale Yeleleh`

# **Tips:**
# • Use `/search` for quick prefix matching
# • Use `/search_full` for broader content search
# • Song titles should include the full path: Artist/Album/Song
# • Use buttons in search results for easy navigation

# **Need Help?**
# If you're having trouble, try:
# 1. Check your spelling
# 2. Use shorter search terms
# 3. Try `/search_full` for broader results
# 4. Use `/artists` to see available artists

# Type `/start` to return to the main menu!
#         """
        
#         await update.effective_message.reply_text(
#             help_message,
#             parse_mode='Markdown'
#         )
    
#     async def handle_inline_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
#         """Handle inline queries for quick search"""
#         query = update.inline_query.query
#         if not query:
#             return
        
#         try:
#             # Perform search
#             results = await self.api_client.search_prefix(query, limit=5)
            
#             if not results.data:
#                 return
            
#             # Create inline results
#             inline_results = []
#             for i, result in enumerate(results.data[:5]):
#                 # Determine result type
#                 slash_count = result.title.count("/")
                
#                 if slash_count == 0:  # Artist
#                     title = f"👤 {result.title}"
#                     description = "Artist"
#                 elif slash_count == 1:  # Album
#                     album_name = result.title.split("/")[-1]
#                     title = f"💿 {album_name}"
#                     description = "Album"
#                 else:  # Song
#                     song_name = result.title.split("/")[-1]
#                     title = f"🎵 {song_name}"
#                     description = "Song"
                
#                 # Create result
#                 inline_result = InlineQueryResultArticle(
#                     id=str(i),
#                     title=title,
#                     description=description,
#                     input_message_content=InputTextMessageContent(
#                         f"🔍 **Search Result:** {result.title}\n\n"
#                         f"Use `/lyrics {result.title}` to get lyrics or "
#                         f"`/artist {result.title.split('/')[0]}` to browse albums.",
#                         parse_mode='Markdown'
#                     )
#                 )
#                 inline_results.append(inline_result)
            
#             await update.inline_query.answer(inline_results)
        
#         except Exception as e:
#             logger.error(f"Inline query error: {e}")
#             await update.inline_query.answer([])
    
#     async def handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
#         """Handle regular text messages"""
#         if not update.effective_message:
#             return
        
#         user_id = update.effective_user.id
#         text = update.effective_message.text
        
#         # Check if user is in a conversation state
#         if user_id in self.user_states:
#             state = self.user_states[user_id]
            
#             if state.get("waiting_for") == "artist_search":
#                 # User is searching for an artist
#                 await self._handle_artist_search(update, context, text)
#                 del self.user_states[user_id]
#             elif state.get("waiting_for") == "album_search":
#                 # User is searching for an album
#                 await self._handle_album_search(update, context, text)
#                 del self.user_states[user_id]
#             elif state.get("waiting_for") == "song_search":
#                 # User is searching for a song
#                 await self._handle_song_search(update, context, text)
#                 del self.user_states[user_id]
#         else:
#             # No conversation state, show help
#             await update.effective_message.reply_text(
#                 "👋 Hi! I'm Mezmur Bot.\n\n"
#                 "Use `/start` to begin or `/help` for commands.\n\n"
#                 "You can search for artists, albums, and songs!",
#                 parse_mode='Markdown'
#             )
    
#     async def _handle_artist_search(self, update: Update, context: ContextTypes.DEFAULT_TYPE, query: str):
#         """Handle artist search from text message"""
#         # Create a mock context with args
#         class MockContext:
#             def __init__(self, query):
#                 self.args = query.split()
        
#         mock_context = MockContext(query)
#         await self.album_commands.artist_command(update, mock_context)
    
#     async def _handle_album_search(self, update: Update, context: ContextTypes.DEFAULT_TYPE, query: str):
#         """Handle album search from text message"""
#         # Create a mock context with args
#         class MockContext:
#             def __init__(self, query):
#                 self.args = query.split()
        
#         mock_context = MockContext(query)
#         await self.album_commands.album_command(update, mock_context)
    
#     async def _handle_song_search(self, update: Update, context: ContextTypes.DEFAULT_TYPE, query: str):
#         """Handle song search from text message"""
#         # Create a mock context with args
#         class MockContext:
#             def __init__(self, query):
#                 self.args = query.split()
        
#         mock_context = MockContext(query)
#         await self.lyrics_commands.lyrics_command(update, mock_context)
    
#     async def run(self):
#         """Run the bot"""
#         try:
#             # Set bot commands
#             commands = [
#                 BotCommand("start", "Start the bot"),
#                 BotCommand("help", "Show help information"),
#                 BotCommand("search", "Fast prefix search"),
#                 BotCommand("search_full", "Broader search"),
#                 BotCommand("lyrics", "Get song lyrics"),
#                 BotCommand("rich_lyrics", "Get rich lyrics"),
#                 BotCommand("random_lyrics", "Get random lyrics"),
#                 BotCommand("artist", "Find albums by artist"),
#                 BotCommand("album", "Find songs in album"),
#                 BotCommand("artists", "List all artists"),
#             ]
            
#             await self.application.bot.set_my_commands(commands)
            
#             # Start the bot
#             logger.info("Starting Mezmur Bot...")
#             await self.application.run_polling()
        
#         except Exception as e:
#             logger.error(f"Bot error: {e}")
#             raise
#         finally:
#             # Clean up
#             await self.api_client.close()


# async def main():
#     """Main function"""
#     bot = MezmurBot(BOT_TOKEN, API_BASE_URL)
#     await bot.run()


# if __name__ == "__main__":
#     asyncio.run(main())
