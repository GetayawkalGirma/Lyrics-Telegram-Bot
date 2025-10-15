"""
Lyrics handlers for the Telegram bot
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.api_client import MezmurAPIClient


class LyricsHandler:
    """Handler for lyrics-related commands"""
    
    def __init__(self, api_client: MezmurAPIClient):
        self.api_client = api_client
    
    async def lyrics_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /lyrics command"""
        if not update.effective_message:
            return
            
        if not context.args:
            await update.effective_message.reply_text(
                "🎵 **Lyrics Command**\n\n"
                "Usage: `/lyrics <song_title>`\n"
                "Example: `/lyrics Samuel Tesfamichael/Misale Yeleleh/Yekebere`\n\n"
                "Get the lyrics for a specific song.",
                parse_mode='Markdown'
            )
            return
        
        song_title = " ".join(context.args)
        await self._get_lyrics(update, context, song_title, rich=False)
    
    async def rich_lyrics_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /rich_lyrics command"""
        if not update.effective_message:
            return
            
        if not context.args:
            await update.effective_message.reply_text(
                "🎵 **Rich Lyrics Command**\n\n"
                "Usage: `/rich_lyrics <song_title>`\n"
                "Example: `/rich_lyrics Samuel Tesfamichael/Misale Yeleleh/Yekebere`\n\n"
                "Get the lyrics with full HTML formatting for a specific song.",
                parse_mode='Markdown'
            )
            return
        
        song_title = " ".join(context.args)
        await self._get_lyrics(update, context, song_title, rich=True)
    
    async def _get_lyrics(self, update: Update, context: ContextTypes.DEFAULT_TYPE, song_title: str, rich: bool = False):
        """Get lyrics for a song"""
        if not update.effective_message or not update.effective_chat:
            return
            
        try:
            # Show typing indicator
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
            
            if rich:
                # Get rich lyrics with HTML formatting
                lyrics = await self.api_client.get_rich_lyrics(song_title)
                await self._send_rich_lyrics(update, context, lyrics)
            else:
                # Get plain text lyrics
                lyrics_data = await self.api_client.get_lyrics(song_title)
                await self._send_plain_lyrics(update, context, lyrics_data)
        
        except Exception as e:
            await update.effective_message.reply_text(
                f"❌ Failed to get lyrics: {str(e)}\n\n"
                "Please check the song title and try again.",
                parse_mode='Markdown'
            )
    
    async def _send_plain_lyrics(self, update: Update, context: ContextTypes.DEFAULT_TYPE, lyrics_data: dict):
        """Send plain text lyrics"""
        if not update.effective_message or not update.effective_chat:
            return
        title = lyrics_data.get("title", "Unknown Song")
        lyrics_text = lyrics_data.get("lyrics", "No lyrics available")
        artist = lyrics_data.get("artist", "")
        album = lyrics_data.get("album", "")
        
        # Create message
        message = f"🎵 **{title}**\n"
        if artist:
            message += f"👤 by {artist}\n"
        if album:
            message += f"💿 from {album}\n"
        message += "\n" + "="*30 + "\n\n"
        message += lyrics_text
        
        # Check message length
        if len(message) > 4000:
            # Send basic info first
            basic_info = f"🎵 **{title}**\n"
            if artist:
                basic_info += f"👤 by {artist}\n"
            if album:
                basic_info += f"💿 from {album}\n"
            
            await update.effective_message.reply_text(basic_info, parse_mode='Markdown')
            
            # Send lyrics in chunks
            await self._send_long_message(update, context, lyrics_text)
        else:
            await update.effective_message.reply_text(message, parse_mode='Markdown')
    
    async def _send_rich_lyrics(self, update: Update, context: ContextTypes.DEFAULT_TYPE, lyrics):
        """Send rich HTML lyrics"""
        if not update.effective_message or not update.effective_chat:
            return
        # Create message with basic info
        message = f"🎵 **{lyrics.title}**\n"
        if lyrics.artist:
            message += f"👤 by {lyrics.artist}\n"
        if lyrics.album:
            message += f"💿 from {lyrics.album}\n"
        
        # Send basic info first
        await update.effective_message.reply_text(message, parse_mode='Markdown')
        
        # Send HTML content
        if len(lyrics.html_content) > 4000:
            await self._send_long_html_message(update, context, lyrics.html_content)
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=lyrics.html_content,
                parse_mode='HTML'
            )
    
    async def _send_long_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
        """Send a long message in chunks"""
        if not update.effective_message or not update.effective_chat:
            return
        max_length = 4000
        chunks = [text[i:i+max_length] for i in range(0, len(text), max_length)]
        
        for i, chunk in enumerate(chunks):
            if i == 0:
                await update.effective_message.reply_text(chunk, parse_mode='Markdown')
            else:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=chunk,
                    parse_mode='Markdown'
                )
    
    async def _send_long_html_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE, html_text: str):
        """Send a long HTML message in chunks"""
        if not update.effective_message or not update.effective_chat:
            return
        max_length = 4000
        
        # Try to split at HTML boundaries
        chunks = []
        current_chunk = ""
        
        # Simple splitting by paragraphs or divs
        parts = html_text.split('</p>')
        
        for part in parts:
            if len(current_chunk + part + '</p>') > max_length and current_chunk:
                chunks.append(current_chunk)
                current_chunk = part + '</p>'
            else:
                current_chunk += part + '</p>'
        
        if current_chunk:
            chunks.append(current_chunk)
        
        for i, chunk in enumerate(chunks):
            if i == 0:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=chunk,
                    parse_mode='HTML'
                )
            else:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=chunk,
                    parse_mode='HTML'
                )
    
    async def random_lyrics_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /random_lyrics command - get random lyrics"""
        if not update.effective_message or not update.effective_chat:
            return
            
        try:
            # Show typing indicator
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
            
            # Get random artists first
            artists_result = await self.api_client.get_artists(limit=4)
            
            if not artists_result.data:
                await update.effective_message.reply_text(
                    "❌ No artists found. Please try again later.",
                    parse_mode='Markdown'
                )
                return
            
            # Get albums for the first artist
            import random
            artist = random.choice(artists_result.data)
            albums_result = await self.api_client.get_artist_albums(artist.title, limit=1)
            
            if not albums_result.data:
                await update.effective_message.reply_text(
                    f"❌ No albums found for {artist.title}",
                    parse_mode='Markdown'
                )
                return
            
            # Get songs for the first album
            album = random.choice(albums_result.data)
            songs_result = await self.api_client.get_album_songs(album.title, limit=1)
            
            if not songs_result.data:
                await update.effective_message.reply_text(
                    f"❌ No songs found for {album.title}",
                    parse_mode='Markdown'
                )
                return
            
            # Get lyrics for the first song
            song = songs_result.data[0]
            await self._get_lyrics(update, context, song.title, rich=True)
        
        except Exception as e:
            await update.effective_message.reply_text(
                f"❌ Failed to get random lyrics: {str(e)}",
                parse_mode='Markdown'
            )
