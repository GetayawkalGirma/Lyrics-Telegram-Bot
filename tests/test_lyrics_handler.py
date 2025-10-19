"""
Tests for the LyricsHandler class
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from handlers.lyrics import LyricsHandler
# Lyrics data is returned as Dict[str, Any] from API


class TestLyricsHandler:
    """Test cases for LyricsHandler class"""
    
    def test_lyrics_handler_initialization(self, mock_api_client):
        """Test LyricsHandler initialization"""
        handler = LyricsHandler(mock_api_client)
        assert handler.api_client == mock_api_client
    
    @pytest.mark.asyncio
    async def test_lyrics_command_no_args(self, mock_update, mock_message, mock_context):
        """Test /lyrics command with no arguments"""
        mock_context.args = []
        
        handler = LyricsHandler(AsyncMock())
        await handler.lyrics_command(mock_update, mock_context)
        
        # Verify usage message was sent
        mock_message.reply_text.assert_called_once()
        call_args = mock_message.reply_text.call_args
        assert "Lyrics Command" in call_args[0][0]
        assert "Usage: `/lyrics <song_title>`" in call_args[0][0]
        assert call_args[1]['parse_mode'] == 'Markdown'
    
    @pytest.mark.asyncio
    async def test_lyrics_command_success(self, mock_update, mock_message, mock_context, mock_lyrics_data, mock_api_client):
        """Test successful /lyrics command"""
        mock_context.args = ["Samuel Tesfamichael/Misale Yeleleh/Yekebere"]
        mock_api_client.get_lyrics.return_value = {
            "title": "Yekebere",
            "artist": "Samuel Tesfamichael",
            "album": "Misale Yeleleh",
            "lyrics": "Yekebere yekebere...\nBeautiful lyrics here..."
        }
        
        handler = LyricsHandler(mock_api_client)
        await handler.lyrics_command(mock_update, mock_context)
        
        # Verify API was called with correct parameters
        mock_api_client.get_lyrics.assert_called_once_with("Samuel Tesfamichael/Misale Yeleleh/Yekebere")
        
        # Verify message was sent with lyrics
        mock_message.reply_text.assert_called_once()
        call_args = mock_message.reply_text.call_args
        assert "Yekebere" in call_args[0][0]
        assert "Samuel Tesfamichael" in call_args[0][0]
        assert "Yekebere yekebere" in call_args[0][0]
        assert call_args[1]['parse_mode'] == 'Markdown'
    
    @pytest.mark.asyncio
    async def test_lyrics_command_not_found(self, mock_update, mock_message, mock_context, mock_api_client):
        """Test /lyrics command when song not found"""
        mock_context.args = ["Nonexistent/Song"]
        mock_api_client.get_lyrics.side_effect = Exception("Song not found")
        
        handler = LyricsHandler(mock_api_client)
        await handler.lyrics_command(mock_update, mock_context)
        
        # Verify error message was sent
        mock_message.reply_text.assert_called_once()
        call_args = mock_message.reply_text.call_args
        assert "Error getting lyrics" in call_args[0][0]
        assert call_args[1]['parse_mode'] == 'Markdown'
    
    @pytest.mark.asyncio
    async def test_rich_lyrics_command_no_args(self, mock_update, mock_message, mock_context):
        """Test /rich_lyrics command with no arguments"""
        mock_context.args = []
        
        handler = LyricsHandler(AsyncMock())
        await handler.rich_lyrics_command(mock_update, mock_context)
        
        # Verify usage message was sent
        mock_message.reply_text.assert_called_once()
        call_args = mock_message.reply_text.call_args
        assert "Rich Lyrics Command" in call_args[0][0]
        assert "Usage: `/rich_lyrics <song_title>`" in call_args[0][0]
    
    @pytest.mark.asyncio
    async def test_rich_lyrics_command_success(self, mock_update, mock_message, mock_context, mock_api_client):
        """Test successful /rich_lyrics command"""
        mock_context.args = ["Samuel Tesfamichael/Misale Yeleleh/Yekebere"]
        mock_api_client.get_lyrics.return_value = {
            "title": "Yekebere",
            "artist": "Samuel Tesfamichael",
            "album": "Misale Yeleleh",
            "lyrics": "Yekebere yekebere...\nBeautiful lyrics here..."
        }
        
        handler = LyricsHandler(mock_api_client)
        await handler.rich_lyrics_command(mock_update, mock_context)
        
        # Verify API was called
        mock_api_client.get_lyrics.assert_called_once_with("Samuel Tesfamichael/Misale Yeleleh/Yekebere")
        
        # Verify message was sent with HTML formatted lyrics
        mock_message.reply_text.assert_called_once()
        call_args = mock_message.reply_text.call_args
        assert "Yekebere" in call_args[0][0]
        assert call_args[1]['parse_mode'] == 'HTML'
    
    @pytest.mark.asyncio
    async def test_random_lyrics_command_success(self, mock_update, mock_message, mock_context, mock_api_client):
        """Test successful /random_lyrics command"""
        mock_api_client.get_random_lyrics.return_value = {
            "title": "Random Song",
            "artist": "Random Artist",
            "album": "Random Album",
            "lyrics": "Random lyrics content..."
        }
        
        handler = LyricsHandler(mock_api_client)
        await handler.random_lyrics_command(mock_update, mock_context)
        
        # Verify API was called
        mock_api_client.get_random_lyrics.assert_called_once()
        
        # Verify message was sent with random lyrics
        mock_message.reply_text.assert_called_once()
        call_args = mock_message.reply_text.call_args
        assert "Random Song" in call_args[0][0]
        assert "Random Artist" in call_args[0][0]
        assert call_args[1]['parse_mode'] == 'Markdown'
    
    @pytest.mark.asyncio
    async def test_random_lyrics_command_error(self, mock_update, mock_message, mock_context, mock_api_client):
        """Test /random_lyrics command with API error"""
        mock_api_client.get_random_lyrics.side_effect = Exception("API Error")
        
        handler = LyricsHandler(mock_api_client)
        await handler.random_lyrics_command(mock_update, mock_context)
        
        # Verify error message was sent
        mock_message.reply_text.assert_called_once()
        call_args = mock_message.reply_text.call_args
        assert "Error getting random lyrics" in call_args[0][0]
        assert call_args[1]['parse_mode'] == 'Markdown'
    
    def test_format_lyrics_plain(self, mock_lyrics_data):
        """Test plain text lyrics formatting"""
        handler = LyricsHandler(AsyncMock())
        
        formatted = handler._format_lyrics(mock_lyrics_data, format_type="plain")
        
        assert "Yekebere" in formatted
        assert "Samuel Tesfamichael" in formatted
        assert "Misale Yeleleh" in formatted
        assert "Yekebere yekebere" in formatted
        assert "=" in formatted  # Separator line
    
    def test_format_lyrics_html(self, mock_lyrics_data):
        """Test HTML lyrics formatting"""
        handler = LyricsHandler(AsyncMock())
        
        formatted = handler._format_lyrics(mock_lyrics_data, format_type="html")
        
        assert "<b>Yekebere</b>" in formatted
        assert "<i>by Samuel Tesfamichael</i>" in formatted
        assert "<i>from Misale Yeleleh</i>" in formatted
        assert "<br>" in formatted  # Line breaks
    
    def test_format_lyrics_with_missing_fields(self):
        """Test lyrics formatting with missing optional fields"""
        handler = LyricsHandler(AsyncMock())
        
        # Create lyrics data with missing album
        lyrics_data = {
            "title": "Test Song",
            "artist": "Test Artist",
            "album": "",  # Empty album
            "lyrics": "Test lyrics"
        }
        
        formatted = handler._format_lyrics(lyrics_data, format_type="plain")
        
        assert "Test Song" in formatted
        assert "Test Artist" in formatted
        assert "Test lyrics" in formatted
        # Should not include album line since it's empty
        assert "from" not in formatted
    
    def test_format_lyrics_long_content(self):
        """Test lyrics formatting with very long content"""
        handler = LyricsHandler(AsyncMock())
        
        # Create lyrics with very long content
        long_lyrics = "A" * 5000  # Very long lyrics
        lyrics_data = {
            "title": "Long Song",
            "artist": "Test Artist",
            "album": "Test Album",
            "lyrics": long_lyrics
        }
        
        formatted = handler._format_lyrics(lyrics_data, format_type="plain")
        
        # Should be truncated
        assert len(formatted) < len(long_lyrics) + 200  # Some overhead for formatting
        assert "truncated" in formatted.lower()
    
    def test_escape_html(self):
        """Test HTML escaping functionality"""
        handler = LyricsHandler(AsyncMock())
        
        # Test various HTML characters
        test_text = "Test & <b>bold</b> & 'quotes' & \"double quotes\""
        escaped = handler._escape_html(test_text)
        
        assert "&amp;" in escaped
        assert "&lt;b&gt;" in escaped
        assert "&quot;" in escaped
        assert "&#x27;" in escaped  # Single quote
    
    def test_clean_lyrics_text(self):
        """Test lyrics text cleaning functionality"""
        handler = LyricsHandler(AsyncMock())
        
        # Test with various whitespace and formatting
        dirty_text = "  Line 1  \n\n  Line 2  \n  \n  Line 3  "
        cleaned = handler._clean_lyrics_text(dirty_text)
        
        # Should remove extra whitespace and empty lines
        lines = cleaned.split('\n')
        assert len(lines) == 3
        assert lines[0] == "Line 1"
        assert lines[1] == "Line 2"
        assert lines[2] == "Line 3"
