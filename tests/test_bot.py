"""
Tests for the main MezmurBot class
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from bot import MezmurBot


class TestMezmurBot:
    """Test cases for MezmurBot class"""
    
    def test_bot_initialization(self, mock_api_client):
        """Test bot initialization with valid parameters"""
        bot_token = "test_token"
        api_base_url = "http://test.api"
        
        with patch('bot.MezmurAPIClient', return_value=mock_api_client), \
             patch('bot.SearchHandler'), \
             patch('bot.LyricsHandler'), \
             patch('bot.AlbumsHandler'), \
             patch('bot.Application'):
            
            bot = MezmurBot(bot_token, api_base_url)
            
            assert bot.bot_token == bot_token
            assert bot.api_base_url == api_base_url
            assert bot.user_states == {}
    
    @pytest.mark.asyncio
    async def test_start_command(self, mock_update, mock_message, mock_user, mock_chat):
        """Test /start command functionality"""
        with patch('bot.MezmurAPIClient'), \
             patch('bot.SearchHandler'), \
             patch('bot.LyricsHandler'), \
             patch('bot.AlbumsHandler'), \
             patch('bot.Application'):
            
            bot = MezmurBot("test_token", "http://test.api")
            await bot.start_command(mock_update, None)
            
            # Verify that reply_text was called with welcome message
            mock_message.reply_text.assert_called_once()
            call_args = mock_message.reply_text.call_args
            assert "Welcome to Mezmur Bot!" in call_args[0][0]
            assert call_args[1]['parse_mode'] == 'Markdown'
            assert 'reply_markup' in call_args[1]
    
    @pytest.mark.asyncio
    async def test_help_command(self, mock_update, mock_message):
        """Test /help command functionality"""
        with patch('bot.MezmurAPIClient'), \
             patch('bot.SearchHandler'), \
             patch('bot.LyricsHandler'), \
             patch('bot.AlbumsHandler'), \
             patch('bot.Application'):
            
            bot = MezmurBot("test_token", "http://test.api")
            await bot.help_command(mock_update, None)
            
            # Verify that reply_text was called with help message
            mock_message.reply_text.assert_called_once()
            call_args = mock_message.reply_text.call_args
            assert "Mezmur Bot Help" in call_args[0][0]
            assert call_args[1]['parse_mode'] == 'Markdown'
    
    @pytest.mark.asyncio
    async def test_handle_button_callback_search_artist(self, mock_callback_query, mock_context):
        """Test artist search button callback"""
        mock_callback_query.data = "search_artist"
        
        # Create a mock update with the callback query
        mock_update = MagicMock()
        mock_update.callback_query = mock_callback_query
        
        with patch('bot.MezmurAPIClient'), \
             patch('bot.SearchHandler'), \
             patch('bot.LyricsHandler'), \
             patch('bot.AlbumsHandler'), \
             patch('bot.Application'):
            
            bot = MezmurBot("test_token", "http://test.api")
            await bot.handle_button_callback(mock_update, mock_context)
            
            # Verify callback was answered
            mock_callback_query.answer.assert_called_once()
            
            # Verify user state was set
            assert bot.user_states[mock_callback_query.from_user.id] == 'waiting_for_artist'
            
            # Verify message was sent
            mock_callback_query.message.reply_text.assert_called_once()
            call_args = mock_callback_query.message.reply_text.call_args
            assert "Search Artists" in call_args[0][0]
    
    @pytest.mark.asyncio
    async def test_handle_button_callback_search_album(self, mock_callback_query, mock_context):
        """Test album search button callback"""
        mock_callback_query.data = "search_album"
        
        # Create a mock update with the callback query
        mock_update = MagicMock()
        mock_update.callback_query = mock_callback_query
        
        with patch('bot.MezmurAPIClient'), \
             patch('bot.SearchHandler'), \
             patch('bot.LyricsHandler'), \
             patch('bot.AlbumsHandler'), \
             patch('bot.Application'):
            
            bot = MezmurBot("test_token", "http://test.api")
            await bot.handle_button_callback(mock_update, mock_context)
            
            # Verify user state was set
            assert bot.user_states[mock_callback_query.from_user.id] == 'waiting_for_album'
    
    @pytest.mark.asyncio
    async def test_handle_button_callback_search_song(self, mock_callback_query, mock_context):
        """Test song search button callback"""
        mock_callback_query.data = "search_song"
        
        # Create a mock update with the callback query
        mock_update = MagicMock()
        mock_update.callback_query = mock_callback_query
        
        with patch('bot.MezmurAPIClient'), \
             patch('bot.SearchHandler'), \
             patch('bot.LyricsHandler'), \
             patch('bot.AlbumsHandler'), \
             patch('bot.Application'):
            
            bot = MezmurBot("test_token", "http://test.api")
            await bot.handle_button_callback(mock_update, mock_context)
            
            # Verify user state was set
            assert bot.user_states[mock_callback_query.from_user.id] == 'waiting_for_song_search'
    
    @pytest.mark.asyncio
    async def test_handle_button_callback_inline_search(self, mock_callback_query, mock_context):
        """Test inline search button callback"""
        mock_callback_query.data = "inline_search"
        
        # Create a mock update with the callback query
        mock_update = MagicMock()
        mock_update.callback_query = mock_callback_query
        
        with patch('bot.MezmurAPIClient'), \
             patch('bot.SearchHandler'), \
             patch('bot.LyricsHandler'), \
             patch('bot.AlbumsHandler'), \
             patch('bot.Application'):
            
            bot = MezmurBot("test_token", "http://test.api")
            await bot.handle_button_callback(mock_update, mock_context)
            
            # Verify message was sent with inline search instructions
            mock_callback_query.message.reply_text.assert_called_once()
            call_args = mock_callback_query.message.reply_text.call_args
            assert "Quick Search Mode" in call_args[0][0]
            assert "@mezmurlybot" in call_args[0][0]
    
    @pytest.mark.asyncio
    async def test_handle_button_callback_back_to_home(self, mock_callback_query, mock_context):
        """Test back to home button callback"""
        mock_callback_query.data = "back_to_home"
        
        # Create a mock update with the callback query
        mock_update = MagicMock()
        mock_update.callback_query = mock_callback_query
        
        with patch('bot.MezmurAPIClient'), \
             patch('bot.SearchHandler'), \
             patch('bot.LyricsHandler'), \
             patch('bot.AlbumsHandler'), \
             patch('bot.Application'):
            
            bot = MezmurBot("test_token", "http://test.api")
            # Set a user state first
            bot.user_states[mock_callback_query.from_user.id] = 'waiting_for_artist'
            
            await bot.handle_button_callback(mock_update, mock_context)
            
            # Verify user state was cleared
            assert mock_callback_query.from_user.id not in bot.user_states
            
            # Verify welcome message was sent
            mock_callback_query.message.reply_text.assert_called_once()
            call_args = mock_callback_query.message.reply_text.call_args
            assert "Welcome to Mezmur Bot!" in call_args[0][0]
    
    @pytest.mark.asyncio
    async def test_handle_text_message_waiting_for_artist(self, mock_update, mock_message, mock_context):
        """Test text message handling when user is waiting for artist name"""
        mock_message.text = "Samuel Tesfamichael"
        # Don't try to set user ID directly, use the fixture's user ID
        
        with patch('bot.MezmurAPIClient'), \
             patch('bot.SearchHandler') as mock_search_handler, \
             patch('bot.LyricsHandler'), \
             patch('bot.AlbumsHandler') as mock_albums_handler, \
             patch('bot.Application'):
            
            bot = MezmurBot("test_token", "http://test.api")
            # Set user state using the fixture's user ID
            user_id = mock_update.effective_user.id
            bot.user_states[user_id] = 'waiting_for_artist'
            
            # Mock the artist command
            mock_albums_handler.return_value.artist_command = AsyncMock()
            
            await bot.handle_text_message(mock_update, mock_context)
            
            # Verify user state was cleared
            assert user_id not in bot.user_states
            
            # Verify artist command was called
            mock_albums_handler.return_value.artist_command.assert_called_once_with(mock_update, mock_context)
            assert mock_context.args == ["Samuel Tesfamichael"]
    
    @pytest.mark.asyncio
    async def test_handle_text_message_waiting_for_album(self, mock_update, mock_message, mock_context):
        """Test text message handling when user is waiting for album name"""
        mock_message.text = "Samuel Tesfamichael/Misale Yeleleh"
        
        with patch('bot.MezmurAPIClient'), \
             patch('bot.SearchHandler'), \
             patch('bot.LyricsHandler'), \
             patch('bot.AlbumsHandler') as mock_albums_handler, \
             patch('bot.Application'):
            
            bot = MezmurBot("test_token", "http://test.api")
            # Set user state using the fixture's user ID
            user_id = mock_update.effective_user.id
            bot.user_states[user_id] = 'waiting_for_album'
            
            # Mock the album command
            mock_albums_handler.return_value.album_command = AsyncMock()
            
            await bot.handle_text_message(mock_update, mock_context)
            
            # Verify album command was called
            mock_albums_handler.return_value.album_command.assert_called_once_with(mock_update, mock_context)
            assert mock_context.args == ["Samuel Tesfamichael/Misale Yeleleh"]
    
    @pytest.mark.asyncio
    async def test_handle_text_message_waiting_for_song_search(self, mock_update, mock_message, mock_context):
        """Test text message handling when user is waiting for song search"""
        mock_message.text = "samuel tesfa"
        
        with patch('bot.MezmurAPIClient'), \
             patch('bot.SearchHandler') as mock_search_handler, \
             patch('bot.LyricsHandler'), \
             patch('bot.AlbumsHandler'), \
             patch('bot.Application'):
            
            bot = MezmurBot("test_token", "http://test.api")
            # Set user state using the fixture's user ID
            user_id = mock_update.effective_user.id
            bot.user_states[user_id] = 'waiting_for_song_search'
            
            # Mock the search command
            mock_search_handler.return_value.search_command = AsyncMock()
            
            await bot.handle_text_message(mock_update, mock_context)
            
            # Verify search command was called
            mock_search_handler.return_value.search_command.assert_called_once_with(mock_update, mock_context)
            assert mock_context.args == ["samuel tesfa"]
    
    @pytest.mark.asyncio
    async def test_handle_text_message_keyword_detection(self, mock_update, mock_message):
        """Test text message handling with keyword detection"""
        # Use a mock object for text instead of a string
        mock_text = MagicMock()
        mock_text.lower.return_value = "samuel tesfamichael"
        mock_message.text = mock_text
        
        with patch('bot.MezmurAPIClient'), \
             patch('bot.SearchHandler'), \
             patch('bot.LyricsHandler'), \
             patch('bot.AlbumsHandler'), \
             patch('bot.Application'):
            
            bot = MezmurBot("test_token", "http://test.api")
            await bot.handle_text_message(mock_update, None)
            
            # Verify helpful message was sent
            mock_message.reply_text.assert_called_once()
            call_args = mock_message.reply_text.call_args
            assert "I detected you might be looking for music!" in call_args[0][0]
    
    @pytest.mark.asyncio
    async def test_handle_text_message_default_response(self, mock_update, mock_message):
        """Test text message handling with default response"""
        # Use a mock object for text instead of a string
        mock_text = MagicMock()
        mock_text.lower.return_value = "hello"
        mock_message.text = mock_text
        
        with patch('bot.MezmurAPIClient'), \
             patch('bot.SearchHandler'), \
             patch('bot.LyricsHandler'), \
             patch('bot.AlbumsHandler'), \
             patch('bot.Application'):
            
            bot = MezmurBot("test_token", "http://test.api")
            await bot.handle_text_message(mock_update, None)
            
            # Verify default message was sent
            mock_message.reply_text.assert_called_once()
            call_args = mock_message.reply_text.call_args
            assert "Hi! I'm Mezmur Bot" in call_args[0][0]
    
    @pytest.mark.asyncio
    async def test_health_check_success(self, mock_api_client):
        """Test successful health check"""
        mock_api_client.health_check.return_value = {"status": "healthy"}
        
        with patch('bot.MezmurAPIClient', return_value=mock_api_client), \
             patch('bot.SearchHandler'), \
             patch('bot.LyricsHandler'), \
             patch('bot.AlbumsHandler'), \
             patch('bot.Application'):
            
            bot = MezmurBot("test_token", "http://test.api")
            result = await bot.health_check()
            
            assert result is True
            mock_api_client.health_check.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_health_check_failure(self, mock_api_client):
        """Test failed health check"""
        mock_api_client.health_check.side_effect = Exception("API Error")
        
        with patch('bot.MezmurAPIClient', return_value=mock_api_client), \
             patch('bot.SearchHandler'), \
             patch('bot.LyricsHandler'), \
             patch('bot.AlbumsHandler'), \
             patch('bot.Application'):
            
            bot = MezmurBot("test_token", "http://test.api")
            result = await bot.health_check()
            
            assert result is False
