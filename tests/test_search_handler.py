"""
Tests for the SearchHandler class
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from handlers.search import SearchHandler
from utils.api_client import SearchResult


class TestSearchHandler:
    """Test cases for SearchHandler class"""
    
    def test_search_handler_initialization(self, mock_api_client):
        """Test SearchHandler initialization"""
        handler = SearchHandler(mock_api_client)
        assert handler.api_client == mock_api_client
    
    @pytest.mark.asyncio
    async def test_search_command_no_args(self, mock_update, mock_message, mock_context):
        """Test /search command with no arguments"""
        mock_context.args = []
        
        handler = SearchHandler(AsyncMock())
        await handler.search_command(mock_update, mock_context)
        
        # Verify usage message was sent
        mock_message.reply_text.assert_called_once()
        call_args = mock_message.reply_text.call_args
        assert "Search Command" in call_args[0][0]
        assert "Usage: `/search <query>`" in call_args[0][0]
        assert call_args[1]['parse_mode'] == 'Markdown'
    
    @pytest.mark.asyncio
    async def test_search_command_success(self, mock_update, mock_message, mock_context, mock_search_results, mock_api_client):
        """Test successful /search command"""
        mock_context.args = ["samuel tesfa"]
        mock_api_client.search_prefix.return_value = MagicMock(data=mock_search_results)
        
        handler = SearchHandler(mock_api_client)
        await handler.search_command(mock_update, mock_context)
        
        # Verify API was called with correct parameters
        mock_api_client.search_prefix.assert_called_once_with("samuel tesfa", limit=10)
        
        # Verify message was sent with results
        mock_message.reply_text.assert_called_once()
        call_args = mock_message.reply_text.call_args
        assert "Search Results" in call_args[0][0]
        assert "Samuel Tesfamichael" in call_args[0][0]
        assert call_args[1]['parse_mode'] == 'Markdown'
        assert 'reply_markup' in call_args[1]
    
    @pytest.mark.asyncio
    async def test_search_command_no_results(self, mock_update, mock_message, mock_context, mock_api_client):
        """Test /search command with no results"""
        mock_context.args = ["nonexistent"]
        mock_api_client.search_prefix.return_value = MagicMock(data=[])
        
        handler = SearchHandler(mock_api_client)
        await handler.search_command(mock_update, mock_context)
        
        # Verify no results message was sent
        mock_message.reply_text.assert_called_once()
        call_args = mock_message.reply_text.call_args
        assert "No results found" in call_args[0][0]
        assert call_args[1]['parse_mode'] == 'Markdown'
    
    @pytest.mark.asyncio
    async def test_search_command_api_error(self, mock_update, mock_message, mock_context, mock_api_client):
        """Test /search command with API error"""
        mock_context.args = ["samuel tesfa"]
        mock_api_client.search_prefix.side_effect = Exception("API Error")
        
        handler = SearchHandler(mock_api_client)
        await handler.search_command(mock_update, mock_context)
        
        # Verify error message was sent
        mock_message.reply_text.assert_called_once()
        call_args = mock_message.reply_text.call_args
        assert "Error searching" in call_args[0][0]
        assert call_args[1]['parse_mode'] == 'Markdown'
    
    @pytest.mark.asyncio
    async def test_search_full_command_no_args(self, mock_update, mock_message, mock_context):
        """Test /search_full command with no arguments"""
        mock_context.args = []
        
        handler = SearchHandler(AsyncMock())
        await handler.search_full_command(mock_update, mock_context)
        
        # Verify usage message was sent
        mock_message.reply_text.assert_called_once()
        call_args = mock_message.reply_text.call_args
        assert "Full Search Command" in call_args[0][0]
        assert "Usage: `/search_full <query>`" in call_args[0][0]
    
    @pytest.mark.asyncio
    async def test_search_full_command_success(self, mock_update, mock_message, mock_context, mock_search_results, mock_api_client):
        """Test successful /search_full command"""
        mock_context.args = ["samuel tesfa"]
        mock_api_client.search_full.return_value = MagicMock(data=mock_search_results)
        
        handler = SearchHandler(mock_api_client)
        await handler.search_full_command(mock_update, mock_context)
        
        # Verify API was called with correct parameters
        mock_api_client.search_full.assert_called_once_with("samuel tesfa", limit=10)
        
        # Verify message was sent with results
        mock_message.reply_text.assert_called_once()
        call_args = mock_message.reply_text.call_args
        assert "Full Search Results" in call_args[0][0]
        assert "Samuel Tesfamichael" in call_args[0][0]
    
    @pytest.mark.asyncio
    async def test_handle_callback_query_search_more(self, mock_callback_query, mock_context, mock_search_results, mock_api_client):
        """Test callback query for 'search_more' action"""
        mock_callback_query.data = "search_more:samuel:1"
        mock_api_client.search_prefix.return_value = MagicMock(data=mock_search_results)
        
        handler = SearchHandler(mock_api_client)
        await handler.handle_callback_query(mock_callback_query, mock_context)
        
        # Verify API was called
        mock_api_client.search_prefix.assert_called_once()
        
        # Verify callback was answered
        mock_callback_query.answer.assert_called_once()
        
        # Verify message was edited
        mock_callback_query.message.edit_text.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_handle_callback_query_unknown_action(self, mock_callback_query, mock_context):
        """Test callback query with unknown action"""
        mock_callback_query.data = "unknown_action"
        
        handler = SearchHandler(AsyncMock())
        await handler.handle_callback_query(mock_callback_query, mock_context)
        
        # Verify callback was answered with error
        mock_callback_query.answer.assert_called_once_with("Unknown action")
    
    @pytest.mark.asyncio
    async def test_handle_callback_query_api_error(self, mock_callback_query, mock_context, mock_api_client):
        """Test callback query with API error"""
        mock_callback_query.data = "search_more:samuel:1"
        mock_api_client.search_prefix.side_effect = Exception("API Error")
        
        handler = SearchHandler(mock_api_client)
        await handler.handle_callback_query(mock_callback_query, mock_context)
        
        # Verify error callback was answered
        mock_callback_query.answer.assert_called_once_with("Error loading more results")
    
    def test_format_search_results(self, mock_search_results):
        """Test search results formatting"""
        handler = SearchHandler(AsyncMock())
        
        # Test with results
        formatted = handler._format_search_results(mock_search_results, "samuel", 0)
        
        assert "Search Results" in formatted
        assert "Samuel Tesfamichael" in formatted
        assert "page 1" in formatted.lower()
        
        # Test with no results
        formatted_empty = handler._format_search_results([], "samuel", 0)
        assert "No results found" in formatted_empty
    
    def test_create_pagination_keyboard(self, mock_search_results):
        """Test pagination keyboard creation"""
        handler = SearchHandler(AsyncMock())
        
        # Test with more results available
        keyboard = handler._create_pagination_keyboard("samuel", 0, len(mock_search_results), 2)
        
        assert len(keyboard) == 1  # One row
        assert len(keyboard[0]) == 1  # One button
        assert "Load More" in keyboard[0][0].text
        
        # Test with no more results
        keyboard_no_more = handler._create_pagination_keyboard("samuel", 0, len(mock_search_results), 10)
        assert keyboard_no_more == []
    
    def test_create_result_keyboard(self, mock_search_results):
        """Test result keyboard creation"""
        handler = SearchHandler(AsyncMock())
        
        keyboard = handler._create_result_keyboard(mock_search_results, "samuel", 0)
        
        # Should have one row per result plus pagination
        assert len(keyboard) >= len(mock_search_results)
        
        # Check that each result has a button
        for i, result in enumerate(mock_search_results):
            song_name = result.title.split("/")[-1]
            found = False
            for row in keyboard:
                for button in row:
                    if song_name in button.text:
                        found = True
                        break
            assert found, f"Button for {song_name} not found"
