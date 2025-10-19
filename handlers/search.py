"""
Search handlers for the Telegram bot
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from typing import List
from utils.api_client import MezmurAPIClient, SearchResult


class SearchHandler:
    """Handler for search-related commands"""
    
    def __init__(self, api_client: MezmurAPIClient):
        self.api_client = api_client
    
    async def search_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /search command - prefix search"""
        if not update.effective_message:
            return
            
        if not context.args:
            await update.effective_message.reply_text(
                "🔍 **Search Command**\n\n"
                "Usage: `/search <query>`\n"
                "Example: `/search samuel tesfa`\n\n"
                "This performs a fast prefix search for titles starting with your query.",
                parse_mode='Markdown'
            )
            return
        
        query = " ".join(context.args)
        await self._perform_search(update, context, query, search_type="prefix")
    
    async def search_full_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /search_full command - full text search"""
        if not update.effective_message:
            return
            
        if not context.args:
            await update.effective_message.reply_text(
                "🔍 **Full Search Command**\n\n"
                "Usage: `/search_full <query>`\n"
                "Example: `/search_full misale`\n\n"
                "This performs a broader search that looks anywhere in content.",
                parse_mode='Markdown'
            )
            return
        
        query = " ".join(context.args)
        await self._perform_search(update, context, query, search_type="full")
    
    async def _perform_search(self, update: Update, context: ContextTypes.DEFAULT_TYPE, query: str, search_type: str):
        """Perform the actual search"""
        if not update.effective_message or not update.effective_chat:
            return
            
        try:
            # Show typing indicator
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
            
            # Perform search
            if search_type == "prefix":
                results = await self.api_client.search_prefix(query, limit=10)
            else:
                results = await self.api_client.search_full(query, limit=10)
            
            if not results.data:
                await update.effective_message.reply_text(
                    f"❌ No results found for '{query}'\n\n"
                    "Try a different search term or use `/search_full` for broader search.",
                    parse_mode='Markdown'
                )
                return
            
            # Format results
            formatted_results = self.api_client.format_search_results(results.data)
            
            # Create response message
            message = f"🔍 **Search Results for '{query}'**\n\n{formatted_results}"
            
            if results.has_next:
                message += f"\n\n📄 Showing {len(results.data)} of {results.total} results"
            
            # Send results
            await update.effective_message.reply_text(message, parse_mode='Markdown')
            
            # If there are results, offer to show more details
            if results.data:
                await self._show_result_actions(update, context, results.data[:5])  # Show first 5 results
        
        except Exception as e:
            await update.effective_message.reply_text(
                f"❌ Search failed: {str(e)}\n\n"
                "Please try again later or contact support if the problem persists.",
                parse_mode='Markdown'
            )
    
    async def _show_result_actions(self, update: Update, context: ContextTypes.DEFAULT_TYPE, results: List[SearchResult]):
        """Show action buttons for search results"""
        if not update.effective_message or not results:
            return
        
        # Create inline keyboard with result options
        keyboard = []
        
        for i, result in enumerate(results[:5]):  # Limit to 5 results
            # Determine result type and create appropriate button
            slash_count = result.title.count("/")
            
            if slash_count == 0:  # Artist
                button_text = f"👤 {result.title}"
                callback_data = f"artist:{result.title}"
            elif slash_count == 1:  # Album
                album_name = result.title.split("/")[-1]
                button_text = f"💿 {album_name}"
                callback_data = f"album:{result.title}"
            else:  # Song
                song_name = result.title.split("/")[-1]
                button_text = f"🎵 {song_name}"
                callback_data = f"lyrics:{result.title}"
            
            keyboard.append([InlineKeyboardButton(button_text, callback_data=callback_data)])
        
        # Add a "Show More" button if there are more results
        if len(results) > 5:
            keyboard.append([InlineKeyboardButton("📄 Show More Results", callback_data="show_more")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.effective_message.reply_text(
            "🎯 **Choose an option to get more details:**",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle callback queries from inline keyboards"""
        query = update.callback_query
        if not query:
            return
            
        await query.answer()
        
        data = query.data
        if not data:
            return
        
        if data.startswith("artist:"):
            artist_name = data[7:]  # Remove "artist:" prefix
            await self._show_artist_details(query, context, artist_name)
        
        elif data.startswith("album:"):
            album_title = data[6:]  # Remove "album:" prefix
            await self._show_album_details(query, context, album_title)
        
        elif data.startswith("lyrics:"):
            song_title = data[7:]  # Remove "lyrics:" prefix
            await self._show_lyrics(query, context, song_title)
        
        elif data == "show_more":
            await query.edit_message_text(
                "📄 **Show More Results**\n\n"
                "This feature will be implemented in a future update.\n"
                "For now, try refining your search query.",
                parse_mode='Markdown'
            )
    
    async def _show_artist_details(self, query, context: ContextTypes.DEFAULT_TYPE, artist_name: str):
        """Show artist details and albums"""
        try:
            await context.bot.send_chat_action(chat_id=query.message.chat_id, action="typing")
            
            # Get artist albums
            albums_result = await self.api_client.get_artist_albums(artist_name, limit=10)
            
            if not albums_result.data:
                await query.edit_message_text(
                    f"👤 **{artist_name}**\n\n"
                    "No albums found for this artist.",
                    parse_mode='Markdown'
                )
                return
            
            # Format albums
            albums_text = "💿 **Albums:**\n"
            for album in albums_result.data:
                album_name = album.title.split("/")[-1] if "/" in album.title else album.title
                albums_text += f"• {album_name}\n"
            
            message = f"👤 **{artist_name}**\n\n{albums_text}"
            
            if albums_result.has_next:
                message += f"\n\n📄 Showing {len(albums_result.data)} of {albums_result.total} albums"
            
            await query.edit_message_text(message, parse_mode='Markdown')
        
        except Exception as e:
            await query.edit_message_text(
                f"❌ Failed to get artist details: {str(e)}",
                parse_mode='Markdown'
            )
    
    async def _show_album_details(self, query, context: ContextTypes.DEFAULT_TYPE, album_title: str):
        """Show album details and songs"""
        try:
            await context.bot.send_chat_action(chat_id=query.message.chat_id, action="typing")
            
            # Get album songs
            songs_result = await self.api_client.get_album_songs(album_title, limit=10)
            
            if not songs_result.data:
                                # Create keyboard with retry and home options
                keyboard = [
                    [
                        InlineKeyboardButton("🔄 Try Another Artist", callback_data="search_artist"),
                        InlineKeyboardButton("🏠 Back to Home", callback_data="back_to_home")
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text(
                    f"💿 **{album_title}**\n\n"
                    "No songs found for this album.",
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
                return
                
            
            # Format songs
            album_name = album_title.split("/")[-1] if "/" in album_title else album_title
            songs_text = f"💿 **{album_name}**\n\n🎵 **Songs:**\n\n"
            for i, song in enumerate(songs_result.data, 1):
                song_name = song.title.split("/")[-1] if "/" in song.title else song.title
                songs_text += f"{i}. {song_name}\n"
            
            if songs_result.has_next:
                songs_text += f"\n📄 Showing {len(songs_result.data)} of {songs_result.total} songs"
            
            # Create inline keyboard for song selection
            keyboard = []
            for song in songs_result.data[:5]:  # Show first 5 songs
                song_name = song.title.split("/")[-1] if "/" in song.title else song.title
                button_text = f"🎵 {song_name}"
                
                # Construct full path: album_title/song_name
                full_song_path = f"{album_title}/{song_name}"
                callback_data = f"lyrics:{full_song_path}"
                
                print(f"DEBUG: Song button created - Song name: '{song_name}', Album: '{album_title}', Full path: '{full_song_path}', Callback: '{callback_data}'")
                keyboard.append([InlineKeyboardButton(button_text, callback_data=callback_data)])
            
            if len(songs_result.data) > 5:
                keyboard.append([InlineKeyboardButton("📄 Show More Songs", callback_data=f"more_songs:{album_title}")])
            
            # Add back to home button
            keyboard.append([InlineKeyboardButton("🏠 Back to Home", callback_data="back_to_home")])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                songs_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        
        except Exception as e:
            await query.edit_message_text(
                f"❌ Failed to get album details: {str(e)}",
                parse_mode='Markdown'
            )
    
    async def _show_lyrics(self, query, context: ContextTypes.DEFAULT_TYPE, song_title: str):
        """Show song lyrics"""
        try:
            await context.bot.send_chat_action(chat_id=query.message.chat_id, action="typing")
            
            print(f"DEBUG: Lyrics handler called with song_title: '{song_title}'")
            
            # Get regular lyrics
            lyrics_data = await self.api_client.get_lyrics(song_title)
            
            # Extract song info from response
            song_name = lyrics_data.get("title", song_title.split("/")[-1])
            artist = lyrics_data.get("artist", "")
            album = lyrics_data.get("album", "")
            lyrics_text = lyrics_data.get("lyrics", "No lyrics available")
            
            # Create message with lyrics info
            message = f"🎵 **{song_name}**\n"
            if artist:
                message += f"👤 by {artist}\n"
            if album:
                message += f"💿 from {album}\n"
            message += "\n" + "="*30 + "\n\n"
            
            # Add lyrics text
            message += lyrics_text
            
            # Telegram has message length limits, so we might need to split
            if len(message) > 4000:
                # Send basic info first
                basic_info = f"🎵 **{song_name}**\n"
                if artist:
                    basic_info += f"👤 by {artist}\n"
                if album:
                    basic_info += f"💿 from {album}\n"
                
                await query.edit_message_text(basic_info, parse_mode='Markdown')
                

                
                # Send lyrics in a separate message
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text=lyrics_text,
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
            else:
                await query.edit_message_text(message, parse_mode='Markdown')
        
        except Exception as e:
            keyboard = [
                [
                    InlineKeyboardButton("🔄 Try Another Song", callback_data="search_song"),
                    InlineKeyboardButton("🏠 Back to Home", callback_data="back_to_home")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                f"❌ Failed to get lyrics: {str(e)}",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
