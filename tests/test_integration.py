"""
Integration tests for the Mezmur Bot
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from bot import MezmurBot


class TestBotIntegration:
    """Integration tests for the complete bot functionality"""
    
    @pytest.mark.asyncio
    async def test_complete_search_flow(self, mock_update, mock_message, mock_context, mock_search_results, mock_api_client):
        """Test complete search flow from command to results"""
        # Setup
        mock_context.args = ["samuel tesfa"]
        mock_api_client.search_prefix.return_value = MagicMock(data=mock_search_results)
        
        with patch('bot.MezmurAPIClient', return_value=mock_api_client), \
             patch('bot.SearchHandler') as mock_search_handler_class, \
             patch('bot.LyricsHandler'), \
             patch('bot.AlbumsHandler'), \
             patch('bot.Application'):
            
            # Create bot
            bot = MezmurBot("test_token", "http://test.api")
            
            # Mock the search handler
            mock_search_handler = AsyncMock()
            mock_search_handler_class.return_value = mock_search_handler
            
            # Test search command
            await bot.search_handler.search_command(mock_update, mock_context)
            
            # Verify API was called
            mock_api_client.search_prefix.assert_called_once_with("samuel tesfa", limit=10)
    
    @pytest.mark.asyncio
    async def test_complete_lyrics_flow(self, mock_update, mock_message, mock_context, mock_lyrics_data, mock_api_client):
        """Test complete lyrics flow from command to results"""
        # Setup
        mock_context.args = ["Samuel Tesfamichael/Misale Yeleleh/Yekebere"]
        mock_api_client.get_lyrics.return_value = {
            "title": "Yekebere",
            "artist": "Samuel Tesfamichael",
            "album": "Misale Yeleleh",
            "lyrics": "Yekebere yekebere...\nBeautiful lyrics here..."
        }
        
        with patch('bot.MezmurAPIClient', return_value=mock_api_client), \
             patch('bot.SearchHandler'), \
             patch('bot.LyricsHandler') as mock_lyrics_handler_class, \
             patch('bot.AlbumsHandler'), \
             patch('bot.Application'):
            
            # Create bot
            bot = MezmurBot("test_token", "http://test.api")
            
            # Mock the lyrics handler
            mock_lyrics_handler = AsyncMock()
            mock_lyrics_handler_class.return_value = mock_lyrics_handler
            
            # Test lyrics command
            await bot.lyrics_handler.lyrics_command(mock_update, mock_context)
            
            # Verify API was called
            mock_api_client.get_lyrics.assert_called_once_with("Samuel Tesfamichael/Misale Yeleleh/Yekebere")
    
    @pytest.mark.asyncio
    async def test_complete_artist_flow(self, mock_update, mock_message, mock_context, mock_albums, mock_api_client):
        """Test complete artist flow from command to albums"""
        # Setup
        mock_context.args = ["Samuel Tesfamichael"]
        mock_api_client.get_artist_albums.return_value = MagicMock(data=mock_albums)
        
        with patch('bot.MezmurAPIClient', return_value=mock_api_client), \
             patch('bot.SearchHandler'), \
             patch('bot.LyricsHandler'), \
             patch('bot.AlbumsHandler') as mock_albums_handler_class, \
             patch('bot.Application'):
            
            # Create bot
            bot = MezmurBot("test_token", "http://test.api")
            
            # Mock the albums handler
            mock_albums_handler = AsyncMock()
            mock_albums_handler_class.return_value = mock_albums_handler
            
            # Test artist command
            await bot.albums_handler.artist_command(mock_update, mock_context)
            
            # Verify API was called
            mock_api_client.get_artist_albums.assert_called_once_with("Samuel Tesfamichael")
    
    @pytest.mark.asyncio
    async def test_inline_query_flow(self, mock_inline_query, mock_search_results, mock_lyrics_data, mock_api_client):
        """Test complete inline query flow"""
        # Setup
        mock_inline_query.query = "samuel tesfa"
        mock_inline_query.offset = "0"
        mock_api_client.search_prefix.return_value = MagicMock(data=mock_search_results)
        mock_api_client.get_lyrics.return_value = {
            "title": "Yekebere",
            "artist": "Samuel Tesfamichael",
            "album": "Misale Yeleleh",
            "lyrics": "Yekebere yekebere...\nBeautiful lyrics here..."
        }
        
        with patch('bot.MezmurAPIClient', return_value=mock_api_client), \
             patch('bot.SearchHandler'), \
             patch('bot.LyricsHandler'), \
             patch('bot.AlbumsHandler'), \
             patch('bot.Application'):
            
            # Create bot
            bot = MezmurBot("test_token", "http://test.api")
            
            # Test inline query
            await bot.handle_inline_query(mock_inline_query, None)
            
            # Verify search API was called
            mock_api_client.search_prefix.assert_called_once_with("samuel tesfa", limit=80)
            
            # Verify inline query was answered
            mock_inline_query.answer.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_user_state_flow(self, mock_update, mock_message, mock_context, mock_search_results, mock_api_client):
        """Test user state management flow"""
        # Setup
        mock_message.text = "Samuel Tesfamichael"
        mock_update.effective_user.id = 12345
        mock_context.args = []
        mock_api_client.get_artist_albums.return_value = MagicMock(data=[])
        
        with patch('bot.MezmurAPIClient', return_value=mock_api_client), \
             patch('bot.SearchHandler'), \
             patch('bot.LyricsHandler'), \
             patch('bot.AlbumsHandler') as mock_albums_handler_class, \
             patch('bot.Application'):
            
            # Create bot
            bot = MezmurBot("test_token", "http://test.api")
            
            # Mock the albums handler
            mock_albums_handler = AsyncMock()
            mock_albums_handler_class.return_value = mock_albums_handler
            
            # Set user state
            bot.user_states[12345] = 'waiting_for_artist'
            
            # Test text message handling
            await bot.handle_text_message(mock_update, mock_context)
            
            # Verify user state was cleared
            assert 12345 not in bot.user_states
            
            # Verify artist command was called with correct args
            mock_albums_handler.artist_command.assert_called_once()
            call_args = mock_albums_handler.artist_command.call_args
            assert call_args[0][1].args == ["Samuel Tesfamichael"]
    
    @pytest.mark.asyncio
    async def test_button_callback_flow(self, mock_callback_query, mock_context):
        """Test complete button callback flow"""
        mock_callback_query.data = "search_artist"
        
        with patch('bot.MezmurAPIClient'), \
             patch('bot.SearchHandler'), \
             patch('bot.LyricsHandler'), \
             patch('bot.AlbumsHandler'), \
             patch('bot.Application'):
            
            # Create bot
            bot = MezmurBot("test_token", "http://test.api")
            
            # Test button callback
            await bot.handle_button_callback(mock_callback_query, mock_context)
            
            # Verify callback was answered
            mock_callback_query.answer.assert_called_once()
            
            # Verify user state was set
            assert bot.user_states[mock_callback_query.from_user.id] == 'waiting_for_artist'
            
            # Verify message was sent
            mock_callback_query.message.reply_text.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_error_handling_flow(self, mock_update, mock_message, mock_context, mock_api_client):
        """Test error handling throughout the flow"""
        # Setup API error
        mock_context.args = ["samuel tesfa"]
        mock_api_client.search_prefix.side_effect = Exception("API Error")
        
        with patch('bot.MezmurAPIClient', return_value=mock_api_client), \
             patch('bot.SearchHandler') as mock_search_handler_class, \
             patch('bot.LyricsHandler'), \
             patch('bot.AlbumsHandler'), \
             patch('bot.Application'):
            
            # Create bot
            bot = MezmurBot("test_token", "http://test.api")
            
            # Mock the search handler
            mock_search_handler = AsyncMock()
            mock_search_handler_class.return_value = mock_search_handler
            
            # Test search command with error
            await bot.search_handler.search_command(mock_update, mock_context)
            
            # Verify error message was sent
            mock_message.reply_text.assert_called_once()
            call_args = mock_message.reply_text.call_args
            assert "Error searching" in call_args[0][0]
    
    @pytest.mark.asyncio
    async def test_health_check_integration(self, mock_api_client):
        """Test health check integration"""
        mock_api_client.health_check.return_value = {"status": "healthy"}
        
        with patch('bot.MezmurAPIClient', return_value=mock_api_client), \
             patch('bot.SearchHandler'), \
             patch('bot.LyricsHandler'), \
             patch('bot.AlbumsHandler'), \
             patch('bot.Application'):
            
            # Create bot
            bot = MezmurBot("test_token", "http://test.api")
            
            # Test health check
            result = await bot.health_check()
            
            # Verify result
            assert result is True
            mock_api_client.health_check.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_bot_initialization_integration(self):
        """Test complete bot initialization"""
        with patch('bot.MezmurAPIClient') as mock_api_client_class, \
             patch('bot.SearchHandler') as mock_search_handler_class, \
             patch('bot.LyricsHandler') as mock_lyrics_handler_class, \
             patch('bot.AlbumsHandler') as mock_albums_handler_class, \
             patch('bot.Application') as mock_app_class:
            
            # Create bot
            bot = MezmurBot("test_token", "http://test.api")
            
            # Verify all components were initialized
            mock_api_client_class.assert_called_once_with("http://test.api")
            mock_search_handler_class.assert_called_once()
            mock_lyrics_handler_class.assert_called_once()
            mock_albums_handler_class.assert_called_once()
            mock_app_class.builder.assert_called_once()
            
            # Verify bot properties
            assert bot.bot_token == "test_token"
            assert bot.api_base_url == "http://test.api"
            assert bot.user_states == {}
    
    @pytest.mark.asyncio
    async def test_pagination_integration(self, mock_inline_query, mock_search_results, mock_api_client):
        """Test pagination in inline queries"""
        # Setup
        mock_inline_query.query = "samuel"
        mock_inline_query.offset = "5"  # Second page
        mock_api_client.search_prefix.return_value = MagicMock(data=mock_search_results)
        
        with patch('bot.MezmurAPIClient', return_value=mock_api_client), \
             patch('bot.SearchHandler'), \
             patch('bot.LyricsHandler'), \
             patch('bot.AlbumsHandler'), \
             patch('bot.Application'):
            
            # Create bot
            bot = MezmurBot("test_token", "http://test.api")
            
            # Set up cache for pagination
            bot._search_cache = {"search_samuel": mock_search_results * 3}  # 6 total results
            
            # Test inline query with pagination
            await bot.handle_inline_query(mock_inline_query, None)
            
            # Verify inline query was answered
            mock_inline_query.answer.assert_called_once()
            
            # Verify pagination parameters
            call_args = mock_inline_query.answer.call_args
            assert 'next_offset' in call_args[1] or call_args[1]['next_offset'] is None
