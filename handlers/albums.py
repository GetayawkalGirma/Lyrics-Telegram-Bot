"""
Albums handlers for the Telegram bot
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.api_client import MezmurAPIClient


class AlbumsHandler:
    """Handler for albums-related commands"""
    
    def __init__(self, api_client: MezmurAPIClient):
        self.api_client = api_client
    
    async def artist_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /artist command - get albums by artist"""
        if not update.effective_message:
            return
            
        if not context.args:
            await update.effective_message.reply_text(
                "👤 **Artist Command**\n\n"
                "Usage: `/artist <artist_name>`\n"
                "Example: `/artist Samuel Tesfamichael`\n\n"
                "Get all albums by a specific artist.",
                parse_mode='Markdown'
            )
            return
        
        artist_name = " ".join(context.args)
        await self._get_artist_albums(update, context, artist_name)
    
    async def album_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /album command - get songs in album"""
        if not update.effective_message:
            return
            
        if not context.args:
            await update.effective_message.reply_text(
                "💿 **Album Command**\n\n"
                "Usage: `/album <album_title>`\n"
                "Example: `/album Samuel Tesfamichael/Misale Yeleleh`\n\n"
                "Get all songs in a specific album.",
                parse_mode='Markdown'
            )
            return
        
        album_title = " ".join(context.args)
        await self._get_album_songs(update, context, album_title)
    
    async def artists_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /artists command - list all artists"""
        if not update.effective_message or not update.effective_chat:
            return
            
        try:
            # Show typing indicator
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
            
            # Get artists
            artists_result = await self.api_client.get_artists(limit=20)
            
            if not artists_result.data:
                await update.effective_message.reply_text(
                    "❌ No artists found.",
                    parse_mode='Markdown'
                )
                return
            
            # Format artists list
            artists_text = "👤 **Available Artists:**\n\n"
            for i, artist in enumerate(artists_result.data, 1):
                artists_text += f"{i}. {artist.title}\n"
            
            if artists_result.has_next:
                artists_text += f"\n📄 Showing {len(artists_result.data)} of {artists_result.total} artists"
            
            await update.effective_message.reply_text(artists_text, parse_mode='Markdown')
        
        except Exception as e:
            await update.effective_message.reply_text(
                f"❌ Failed to get artists: {str(e)}",
                parse_mode='Markdown'
            )
    
    async def _get_artist_albums(self, update: Update, context: ContextTypes.DEFAULT_TYPE, artist_name: str):
        """Get albums by artist"""
        if not update.effective_message or not update.effective_chat:
            return
            
        try:
            # Show typing indicator
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
            
            # Get artist albums
            albums_result = await self.api_client.get_artist_albums(artist_name, limit=20)
            
            if not albums_result.data:
                # Create keyboard with retry and home options
                keyboard = [
                    [
                        InlineKeyboardButton("🔄 Try Another Artist", callback_data="search_artist"),
                        InlineKeyboardButton("🏠 Back to Home", callback_data="back_to_home")
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.effective_message.reply_text(
                    f"❌ No albums found for '{artist_name}'\n\n"
                    "Please check the artist name and try again.\n\n"
                    "You can try searching for another artist or go back to the main menu.",
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
                return
            
            # Format albums list
            albums_text = f"👤 **{artist_name}**\n\n💿 **Albums:**\n\n"
            for i, album in enumerate(albums_result.data, 1):
                album_name = album.title.split("/")[-1] if "/" in album.title else album.title
                albums_text += f"{i}. {album_name}\n"
            
            if albums_result.has_next:
                albums_text += f"\n📄 Showing {len(albums_result.data)} of {albums_result.total} albums"
            
            # Create inline keyboard for album selection
            keyboard = []
            for album in albums_result.data[:5]:  # Show first 5 albums
                album_name = album.title.split("/")[-1] if "/" in album.title else album.title
                button_text = f"💿 {album_name}"
                callback_data = f"album:{album.title}"
                keyboard.append([InlineKeyboardButton(button_text, callback_data=callback_data)])
            
            if len(albums_result.data) > 5:
                keyboard.append([InlineKeyboardButton("📄 Show More Albums", callback_data=f"more_albums:{artist_name}")])
            
            # Add back to home button
            keyboard.append([InlineKeyboardButton("🏠 Back to Home", callback_data="back_to_home")])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.effective_message.reply_text(
                albums_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        
        except Exception as e:
            await update.effective_message.reply_text(
                f"❌ Failed to get albums for '{artist_name}': {str(e)}",
                parse_mode='Markdown'
            )
    
    async def _get_album_songs(self, update: Update, context: ContextTypes.DEFAULT_TYPE, album_title: str):
        """Get songs in album"""
        if not update.effective_message or not update.effective_chat:
            return
            
        try:
            # Show typing indicator
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
            
            # Get album songs
            songs_result = await self.api_client.get_album_songs(album_title, limit=20)
            
            if not songs_result.data:
                # Create keyboard with retry and home options
                keyboard = [
                    [
                        InlineKeyboardButton("🔄 Try Another Album", callback_data="search_album"),
                        InlineKeyboardButton("🏠 Back to Home", callback_data="back_to_home")
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.effective_message.reply_text(
                    f"❌ No songs found for '{album_title}'\n\n"
                    "Please check the album title and try again.\n\n"
                    "You can try searching for another album or go back to the main menu.",
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
                return
            
            # Format songs list
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
                callback_data = f"lyrics:{song.title}"
                keyboard.append([InlineKeyboardButton(button_text, callback_data=callback_data)])
            
            if len(songs_result.data) > 5:
                keyboard.append([InlineKeyboardButton("📄 Show More Songs", callback_data=f"more_songs:{album_title}")])
            
            # Add back to home button
            keyboard.append([InlineKeyboardButton("🏠 Back to Home", callback_data="back_to_home")])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.effective_message.reply_text(
                songs_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        
        except Exception as e:
            await update.effective_message.reply_text(
                f"❌ Failed to get songs for '{album_title}': {str(e)}",
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
        
        if data.startswith("album:"):
            album_title = data[6:]  # Remove "album:" prefix
            await self._show_album_songs(query, context, album_title)
        
        elif data.startswith("lyrics:"):
            song_title = data[7:]  # Remove "lyrics:" prefix
            await self._show_lyrics(query, context, song_title)
        
        elif data.startswith("more_albums:"):
            artist_name = data[12:]  # Remove "more_albums:" prefix
            await self._show_more_albums(query, context, artist_name)
        
        elif data.startswith("more_songs:"):
            album_title = data[11:]  # Remove "more_songs:" prefix
            await self._show_more_songs(query, context, album_title)
    
    async def _show_album_songs(self, query, context: ContextTypes.DEFAULT_TYPE, album_title: str):
        """Show songs in an album"""
        try:
            await context.bot.send_chat_action(chat_id=query.message.chat_id, action="album songs")
            
            songs_result = await self.api_client.get_album_songs(album_title, limit=15)
            
            if not songs_result.data:
                # Create keyboard with retry and home options
                keyboard = [
                    [
                        InlineKeyboardButton("🔄 Try Another Album", callback_data="search_album"),
                        InlineKeyboardButton("🏠 Back to Home", callback_data="back_to_home")
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(
                    f"💿 **{album_title}**\n\nNo songs found.",
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
                callback_data = f"lyrics:{song.title}"  # Store FULL path for lyrics
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
                f"❌ Failed to get songs: {str(e)}",
                parse_mode='Markdown'
            )
    
    async def _show_lyrics(self, query, context: ContextTypes.DEFAULT_TYPE, song_title: str):
        """Show song lyrics"""
        try:
            await context.bot.send_chat_action(chat_id=query.message.chat_id, action="typing")
            
            lyrics = await self.api_client.get_rich_lyrics(song_title)
            
            # Create message with lyrics info
            message = f"🎵 **{lyrics.title}**\n"
            if lyrics.artist:
                message += f"👤 by {lyrics.artist}\n"
            if lyrics.album:
                message += f"💿 from {lyrics.album}\n"
            message += "\n" + "="*30 + "\n\n"
            
            # Add HTML content
            message += lyrics.html_content
            
            # Check message length
            if len(message) > 4000:
                # Send basic info first
                basic_info = f"🎵 **{lyrics.title}**\n"
                if lyrics.artist:
                    basic_info += f"👤 by {lyrics.artist}\n"
                if lyrics.album:
                    basic_info += f"💿 from {lyrics.album}\n"
                
                await query.edit_message_text(basic_info, parse_mode='Markdown')
                
                # Send lyrics in a separate message
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text=lyrics.html_content,
                    parse_mode='HTML'
                )
            else:
                await query.edit_message_text(message, parse_mode='Markdown')
        
        except Exception as e:
            await query.edit_message_text(
                f"❌ Failed to get lyrics: {str(e)}",
                parse_mode='Markdown'
            )
    
    async def _show_more_albums(self, query, context: ContextTypes.DEFAULT_TYPE, artist_name: str):
        """Show more albums for an artist"""
        await query.edit_message_text(
            f"📄 **More Albums for {artist_name}**\n\n"
            "This feature will be implemented in a future update.\n"
            "For now, try using the `/artist` command with the artist name.",
            parse_mode='Markdown'
        )
    
    async def _show_more_songs(self, query, context: ContextTypes.DEFAULT_TYPE, album_title: str):
        """Show more songs for an album"""
        await query.edit_message_text(
            f"📄 **More Songs for {album_title}**\n\n"
            "This feature will be implemented in a future update.\n"
            "For now, try using the `/album` command with the album title.",
            parse_mode='Markdown'
        )
