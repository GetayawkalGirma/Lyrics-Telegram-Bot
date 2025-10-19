"""
Tests for the AlbumsHandler class
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from handlers.albums import AlbumsHandler
from utils.api_client import Artist, Album, SearchResult


class TestAlbumsHandler:
    """Test cases for AlbumsHandler class"""
    
    def test_albums_handler_initialization(self, mock_api_client):
        """Test AlbumsHandler initialization"""
        handler = AlbumsHandler(mock_api_client)
        assert handler.api_client == mock_api_client
    
    @pytest.mark.asyncio
    async def test_artist_command_no_args(self, mock_update, mock_message, mock_context):
        """Test /artist command with no arguments"""
        mock_context.args = []
        
        handler = AlbumsHandler(AsyncMock())
        await handler.artist_command(mock_update, mock_context)
        
        # Verify usage message was sent
        mock_message.reply_text.assert_called_once()
        call_args = mock_message.reply_text.call_args
        assert "Artist Command" in call_args[0][0]
        assert "Usage: `/artist <artist_name>`" in call_args[0][0]
        assert call_args[1]['parse_mode'] == 'Markdown'
    
    @pytest.mark.asyncio
    async def test_artist_command_success(self, mock_update, mock_message, mock_context, mock_albums, mock_api_client):
        """Test successful /artist command"""
        mock_context.args = ["Samuel Tesfamichael"]
        mock_api_client.get_artist_albums.return_value = MagicMock(data=mock_albums)
        
        handler = AlbumsHandler(mock_api_client)
        await handler.artist_command(mock_update, mock_context)
        
        # Verify API was called with correct parameters
        mock_api_client.get_artist_albums.assert_called_once_with("Samuel Tesfamichael")
        
        # Verify message was sent with albums
        mock_message.reply_text.assert_called_once()
        call_args = mock_message.reply_text.call_args
        assert "Albums by Samuel Tesfamichael" in call_args[0][0]
        assert "Misale Yeleleh" in call_args[0][0]
        assert call_args[1]['parse_mode'] == 'Markdown'
        assert 'reply_markup' in call_args[1]
    
    @pytest.mark.asyncio
    async def test_artist_command_no_albums(self, mock_update, mock_message, mock_context, mock_api_client):
        """Test /artist command when artist has no albums"""
        mock_context.args = ["Unknown Artist"]
        mock_api_client.get_artist_albums.return_value = MagicMock(data=[])
        
        handler = AlbumsHandler(mock_api_client)
        await handler.artist_command(mock_update, mock_context)
        
        # Verify no albums message was sent
        mock_message.reply_text.assert_called_once()
        call_args = mock_message.reply_text.call_args
        assert "No albums found" in call_args[0][0]
        assert call_args[1]['parse_mode'] == 'Markdown'
    
    @pytest.mark.asyncio
    async def test_artist_command_api_error(self, mock_update, mock_message, mock_context, mock_api_client):
        """Test /artist command with API error"""
        mock_context.args = ["Samuel Tesfamichael"]
        mock_api_client.get_artist_albums.side_effect = Exception("API Error")
        
        handler = AlbumsHandler(mock_api_client)
        await handler.artist_command(mock_update, mock_context)
        
        # Verify error message was sent
        mock_message.reply_text.assert_called_once()
        call_args = mock_message.reply_text.call_args
        assert "Error getting albums" in call_args[0][0]
        assert call_args[1]['parse_mode'] == 'Markdown'
    
    @pytest.mark.asyncio
    async def test_album_command_no_args(self, mock_update, mock_message, mock_context):
        """Test /album command with no arguments"""
        mock_context.args = []
        
        handler = AlbumsHandler(AsyncMock())
        await handler.album_command(mock_update, mock_context)
        
        # Verify usage message was sent
        mock_message.reply_text.assert_called_once()
        call_args = mock_message.reply_text.call_args
        assert "Album Command" in call_args[0][0]
        assert "Usage: `/album <album_title>`" in call_args[0][0]
    
    @pytest.mark.asyncio
    async def test_album_command_success(self, mock_update, mock_message, mock_context, mock_search_results, mock_api_client):
        """Test successful /album command"""
        mock_context.args = ["Samuel Tesfamichael/Misale Yeleleh"]
        mock_api_client.get_album_songs.return_value = MagicMock(data=mock_search_results)
        
        handler = AlbumsHandler(mock_api_client)
        await handler.album_command(mock_update, mock_context)
        
        # Verify API was called with correct parameters
        mock_api_client.get_album_songs.assert_called_once_with("Samuel Tesfamichael/Misale Yeleleh")
        
        # Verify message was sent with songs
        mock_message.reply_text.assert_called_once()
        call_args = mock_message.reply_text.call_args
        assert "Songs in Misale Yeleleh" in call_args[0][0]
        assert "Yekebere" in call_args[0][0]
        assert call_args[1]['parse_mode'] == 'Markdown'
        assert 'reply_markup' in call_args[1]
    
    @pytest.mark.asyncio
    async def test_album_command_no_songs(self, mock_update, mock_message, mock_context, mock_api_client):
        """Test /album command when album has no songs"""
        mock_context.args = ["Empty/Album"]
        mock_api_client.get_album_songs.return_value = MagicMock(data=[])
        
        handler = AlbumsHandler(mock_api_client)
        await handler.album_command(mock_update, mock_context)
        
        # Verify no songs message was sent
        mock_message.reply_text.assert_called_once()
        call_args = mock_message.reply_text.call_args
        assert "No songs found" in call_args[0][0]
        assert call_args[1]['parse_mode'] == 'Markdown'
    
    @pytest.mark.asyncio
    async def test_artists_command_success(self, mock_update, mock_message, mock_context, mock_artists, mock_api_client):
        """Test successful /artists command"""
        mock_api_client.get_artists.return_value = MagicMock(data=mock_artists)
        
        handler = AlbumsHandler(mock_api_client)
        await handler.artists_command(mock_update, mock_context)
        
        # Verify API was called
        mock_api_client.get_artists.assert_called_once()
        
        # Verify message was sent with artists
        mock_message.reply_text.assert_called_once()
        call_args = mock_message.reply_text.call_args
        assert "Available Artists" in call_args[0][0]
        assert "Samuel Tesfamichael" in call_args[0][0]
        assert "Getayawkal & Birucktawit" in call_args[0][0]
        assert call_args[1]['parse_mode'] == 'Markdown'
        assert 'reply_markup' in call_args[1]
    
    @pytest.mark.asyncio
    async def test_artists_command_api_error(self, mock_update, mock_message, mock_context, mock_api_client):
        """Test /artists command with API error"""
        mock_api_client.get_artists.side_effect = Exception("API Error")
        
        handler = AlbumsHandler(mock_api_client)
        await handler.artists_command(mock_update, mock_context)
        
        # Verify error message was sent
        mock_message.reply_text.assert_called_once()
        call_args = mock_message.reply_text.call_args
        assert "Error getting artists" in call_args[0][0]
        assert call_args[1]['parse_mode'] == 'Markdown'
    
    @pytest.mark.asyncio
    async def test_handle_callback_query_album_songs(self, mock_callback_query, mock_context, mock_search_results, mock_api_client):
        """Test callback query for album songs"""
        mock_callback_query.data = "album_songs:Samuel Tesfamichael/Misale Yeleleh"
        mock_api_client.get_album_songs.return_value = MagicMock(data=mock_search_results)
        
        handler = AlbumsHandler(mock_api_client)
        await handler.handle_callback_query(mock_callback_query, mock_context)
        
        # Verify API was called
        mock_api_client.get_album_songs.assert_called_once_with("Samuel Tesfamichael/Misale Yeleleh")
        
        # Verify callback was answered
        mock_callback_query.answer.assert_called_once()
        
        # Verify message was edited
        mock_callback_query.message.edit_text.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_handle_callback_query_artist_albums(self, mock_callback_query, mock_context, mock_albums, mock_api_client):
        """Test callback query for artist albums"""
        mock_callback_query.data = "artist_albums:Samuel Tesfamichael"
        mock_api_client.get_artist_albums.return_value = MagicMock(data=mock_albums)
        
        handler = AlbumsHandler(mock_api_client)
        await handler.handle_callback_query(mock_callback_query, mock_context)
        
        # Verify API was called
        mock_api_client.get_artist_albums.assert_called_once_with("Samuel Tesfamichael")
        
        # Verify callback was answered
        mock_callback_query.answer.assert_called_once()
        
        # Verify message was edited
        mock_callback_query.message.edit_text.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_handle_callback_query_unknown_action(self, mock_callback_query, mock_context):
        """Test callback query with unknown action"""
        mock_callback_query.data = "unknown_action"
        
        handler = AlbumsHandler(AsyncMock())
        await handler.handle_callback_query(mock_callback_query, mock_context)
        
        # Verify callback was answered with error
        mock_callback_query.answer.assert_called_once_with("Unknown action")
    
    @pytest.mark.asyncio
    async def test_handle_callback_query_api_error(self, mock_callback_query, mock_context, mock_api_client):
        """Test callback query with API error"""
        mock_callback_query.data = "album_songs:Test/Album"
        mock_api_client.get_album_songs.side_effect = Exception("API Error")
        
        handler = AlbumsHandler(mock_api_client)
        await handler.handle_callback_query(mock_callback_query, mock_context)
        
        # Verify error callback was answered
        mock_callback_query.answer.assert_called_once_with("Error loading content")
    
    def test_format_albums_list(self, mock_albums):
        """Test albums list formatting"""
        handler = AlbumsHandler(AsyncMock())
        
        formatted = handler._format_albums_list(mock_albums, "Samuel Tesfamichael")
        
        assert "Albums by Samuel Tesfamichael" in formatted
        assert "Misale Yeleleh" in formatted
        assert "Enkuan Des Alachehu" in formatted
    
    def test_format_songs_list(self, mock_search_results):
        """Test songs list formatting"""
        handler = AlbumsHandler(AsyncMock())
        
        formatted = handler._format_songs_list(mock_search_results, "Misale Yeleleh")
        
        assert "Songs in Misale Yeleleh" in formatted
        assert "Yekebere" in formatted
        assert "Misale Yeleleh" in formatted
    
    def test_format_artists_list(self, mock_artists):
        """Test artists list formatting"""
        handler = AlbumsHandler(AsyncMock())
        
        formatted = handler._format_artists_list(mock_artists)
        
        assert "Available Artists" in formatted
        assert "Samuel Tesfamichael" in formatted
        assert "Getayawkal & Birucktawit" in formatted
        assert "Tesfaye Chala" in formatted
    
    def test_create_albums_keyboard(self, mock_albums):
        """Test albums keyboard creation"""
        handler = AlbumsHandler(AsyncMock())
        
        keyboard = handler._create_albums_keyboard(mock_albums, "Samuel Tesfamichael")
        
        # Should have one row per album
        assert len(keyboard) == len(mock_albums)
        
        # Check that each album has a button
        for i, album in enumerate(mock_albums):
            album_name = album.title.split("/")[-1]
            found = False
            for row in keyboard:
                for button in row:
                    if album_name in button.text:
                        found = True
                        break
            assert found, f"Button for {album_name} not found"
    
    def test_create_songs_keyboard(self, mock_search_results):
        """Test songs keyboard creation"""
        handler = AlbumsHandler(AsyncMock())
        
        keyboard = handler._create_songs_keyboard(mock_search_results, "Misale Yeleleh")
        
        # Should have one row per song
        assert len(keyboard) == len(mock_search_results)
        
        # Check that each song has a button
        for i, song in enumerate(mock_search_results):
            song_name = song.title.split("/")[-1]
            found = False
            for row in keyboard:
                for button in row:
                    if song_name in button.text:
                        found = True
                        break
            assert found, f"Button for {song_name} not found"
    
    def test_create_artists_keyboard(self, mock_artists):
        """Test artists keyboard creation"""
        handler = AlbumsHandler(AsyncMock())
        
        keyboard = handler._create_artists_keyboard(mock_artists)
        
        # Should have one row per artist
        assert len(keyboard) == len(mock_artists)
        
        # Check that each artist has a button
        for i, artist in enumerate(mock_artists):
            artist_name = artist.title
            found = False
            for row in keyboard:
                for button in row:
                    if artist_name in button.text:
                        found = True
                        break
            assert found, f"Button for {artist_name} not found"
    
    def test_extract_album_name(self):
        """Test album name extraction from full title"""
        handler = AlbumsHandler(AsyncMock())
        
        # Test with full album title
        album_name = handler._extract_album_name("Samuel Tesfamichael/Misale Yeleleh")
        assert album_name == "Misale Yeleleh"
        
        # Test with single name
        album_name = handler._extract_album_name("Misale Yeleleh")
        assert album_name == "Misale Yeleleh"
    
    def test_extract_song_name(self):
        """Test song name extraction from full title"""
        handler = AlbumsHandler(AsyncMock())
        
        # Test with full song title
        song_name = handler._extract_song_name("Samuel Tesfamichael/Misale Yeleleh/Yekebere")
        assert song_name == "Yekebere"
        
        # Test with album/song title
        song_name = handler._extract_song_name("Misale Yeleleh/Yekebere")
        assert song_name == "Yekebere"
        
        # Test with single name
        song_name = handler._extract_song_name("Yekebere")
        assert song_name == "Yekebere"
