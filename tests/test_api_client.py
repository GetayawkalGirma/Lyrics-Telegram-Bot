"""
Tests for the MezmurAPIClient class
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import httpx
from utils.api_client import MezmurAPIClient, SearchResult, Artist, Album, RichLyrics


class TestMezmurAPIClient:
    """Test cases for MezmurAPIClient class"""
    
    def test_api_client_initialization(self):
        """Test API client initialization"""
        base_url = "http://test.api"
        client = MezmurAPIClient(base_url)
        
        assert client.base_url == base_url
        assert client.client is not None
    
    @pytest.mark.asyncio
    async def test_search_prefix_success(self):
        """Test successful prefix search"""
        mock_response = {
            "data": [
                {
                    "title": "Samuel Tesfamichael/Misale Yeleleh/Yekebere",
                    "pageid": 1,
                    "snippet": "Beautiful song",
                    "size": 1500,
                    "wordcount": 200
                }
            ]
        }
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get.return_value.json.return_value = mock_response
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            client = MezmurAPIClient("http://test.api")
            result = await client.search_prefix("samuel", limit=10)
            
            # Verify API call
            mock_client.get.assert_called_once()
            call_args = mock_client.get.call_args
            assert "search/prefix" in call_args[0][0]
            assert call_args[1]['params']['q'] == "samuel"
            assert call_args[1]['params']['limit'] == 10
            
            # Verify result structure
            assert len(result.data) == 1
            assert isinstance(result.data[0], SearchResult)
            assert result.data[0].title == "Samuel Tesfamichael/Misale Yeleleh/Yekebere"
    
    @pytest.mark.asyncio
    async def test_search_prefix_http_error(self):
        """Test prefix search with HTTP error"""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get.side_effect = httpx.HTTPStatusError("Not Found", request=MagicMock(), response=MagicMock())
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            client = MezmurAPIClient("http://test.api")
            
            with pytest.raises(httpx.HTTPStatusError):
                await client.search_prefix("samuel")
    
    @pytest.mark.asyncio
    async def test_search_full_success(self):
        """Test successful full text search"""
        mock_response = {
            "data": [
                {
                    "title": "Samuel Tesfamichael/Misale Yeleleh/Yekebere",
                    "pageid": 1,
                    "snippet": "Beautiful song lyrics",
                    "size": 1500,
                    "wordcount": 200
                }
            ]
        }
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get.return_value.json.return_value = mock_response
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            client = MezmurAPIClient("http://test.api")
            result = await client.search_full("samuel tesfa", limit=5)
            
            # Verify API call
            mock_client.get.assert_called_once()
            call_args = mock_client.get.call_args
            assert "search/full" in call_args[0][0]
            assert call_args[1]['params']['q'] == "samuel tesfa"
            assert call_args[1]['params']['limit'] == 5
    
    @pytest.mark.asyncio
    async def test_get_lyrics_success(self):
        """Test successful lyrics retrieval"""
        mock_response = {
            "title": "Yekebere",
            "artist": "Samuel Tesfamichael",
            "album": "Misale Yeleleh",
            "lyrics": "Yekebere yekebere...\nBeautiful lyrics here..."
        }
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get.return_value.json.return_value = mock_response
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            client = MezmurAPIClient("http://test.api")
            result = await client.get_lyrics("Samuel Tesfamichael/Misale Yeleleh/Yekebere")
            
            # Verify API call
            mock_client.get.assert_called_once()
            call_args = mock_client.get.call_args
            assert "lyrics" in call_args[0][0]
            assert call_args[1]['params']['title'] == "Samuel Tesfamichael/Misale Yeleleh/Yekebere"
            
            # Verify result
            assert result["title"] == "Yekebere"
            assert result["artist"] == "Samuel Tesfamichael"
            assert result["album"] == "Misale Yeleleh"
            assert "Yekebere yekebere" in result["lyrics"]
    
    @pytest.mark.asyncio
    async def test_get_lyrics_not_found(self):
        """Test lyrics retrieval when song not found"""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get.side_effect = httpx.HTTPStatusError("Not Found", request=MagicMock(), response=MagicMock())
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            client = MezmurAPIClient("http://test.api")
            
            with pytest.raises(httpx.HTTPStatusError):
                await client.get_lyrics("Nonexistent/Song")
    
    @pytest.mark.asyncio
    async def test_get_artists_success(self):
        """Test successful artists retrieval"""
        mock_response = {
            "data": [
                {
                    "title": "Samuel Tesfamichael",
                    "pageid": 1,
                    "namespace": 0
                },
                {
                    "title": "Getayawkal & Birucktawit",
                    "pageid": 2,
                    "namespace": 0
                }
            ]
        }
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get.return_value.json.return_value = mock_response
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            client = MezmurAPIClient("http://test.api")
            result = await client.get_artists()
            
            # Verify API call
            mock_client.get.assert_called_once()
            call_args = mock_client.get.call_args
            assert "artists" in call_args[0][0]
            
            # Verify result structure
            assert len(result.data) == 2
            assert isinstance(result.data[0], Artist)
            assert result.data[0].title == "Samuel Tesfamichael"
            assert result.data[1].title == "Getayawkal & Birucktawit"
    
    @pytest.mark.asyncio
    async def test_get_artist_albums_success(self):
        """Test successful artist albums retrieval"""
        mock_response = {
            "data": [
                {
                    "title": "Samuel Tesfamichael/Misale Yeleleh",
                    "pageid": 1,
                    "namespace": 0
                }
            ]
        }
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get.return_value.json.return_value = mock_response
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            client = MezmurAPIClient("http://test.api")
            result = await client.get_artist_albums("Samuel Tesfamichael")
            
            # Verify API call
            mock_client.get.assert_called_once()
            call_args = mock_client.get.call_args
            assert "artist" in call_args[0][0]
            assert call_args[1]['params']['name'] == "Samuel Tesfamichael"
            
            # Verify result structure
            assert len(result.data) == 1
            assert isinstance(result.data[0], Album)
            assert result.data[0].title == "Samuel Tesfamichael/Misale Yeleleh"
    
    @pytest.mark.asyncio
    async def test_get_album_songs_success(self):
        """Test successful album songs retrieval"""
        mock_response = {
            "data": [
                {
                    "title": "Samuel Tesfamichael/Misale Yeleleh/Yekebere",
                    "pageid": 1,
                    "snippet": "Beautiful song",
                    "size": 1500,
                    "wordcount": 200
                }
            ]
        }
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get.return_value.json.return_value = mock_response
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            client = MezmurAPIClient("http://test.api")
            result = await client.get_album_songs("Samuel Tesfamichael/Misale Yeleleh")
            
            # Verify API call
            mock_client.get.assert_called_once()
            call_args = mock_client.get.call_args
            assert "album" in call_args[0][0]
            assert call_args[1]['params']['title'] == "Samuel Tesfamichael/Misale Yeleleh"
            
            # Verify result structure
            assert len(result.data) == 1
            assert isinstance(result.data[0], SearchResult)
            assert result.data[0].title == "Samuel Tesfamichael/Misale Yeleleh/Yekebere"
    
    @pytest.mark.asyncio
    async def test_health_check_success(self):
        """Test successful health check"""
        mock_response = {"status": "healthy", "version": "1.0.0"}
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get.return_value.json.return_value = mock_response
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            client = MezmurAPIClient("http://test.api")
            result = await client.health_check()
            
            # Verify API call
            mock_client.get.assert_called_once()
            call_args = mock_client.get.call_args
            assert "health" in call_args[0][0]
            
            # Verify result
            assert result == mock_response
    
    @pytest.mark.asyncio
    async def test_health_check_failure(self):
        """Test health check failure"""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get.side_effect = httpx.HTTPStatusError("Service Unavailable", request=MagicMock(), response=MagicMock())
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            client = MezmurAPIClient("http://test.api")
            
            with pytest.raises(httpx.HTTPStatusError):
                await client.health_check()
    
    @pytest.mark.asyncio
    async def test_close(self):
        """Test client close method"""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            client = MezmurAPIClient("http://test.api")
            await client.close()
            
            # Verify client was closed
            mock_client.aclose.assert_called_once()
    
    def test_search_result_dataclass(self):
        """Test SearchResult dataclass"""
        result = SearchResult(
            title="Test Song",
            pageid=123,
            snippet="Test snippet",
            size=1000,
            wordcount=150
        )
        
        assert result.title == "Test Song"
        assert result.pageid == 123
        assert result.snippet == "Test snippet"
        assert result.size == 1000
        assert result.wordcount == 150
    
    def test_artist_dataclass(self):
        """Test Artist dataclass"""
        artist = Artist(title="Test Artist", pageid=456, namespace=0)
        
        assert artist.title == "Test Artist"
        assert artist.pageid == 456
        assert artist.namespace == 0
    
    def test_album_dataclass(self):
        """Test Album dataclass"""
        album = Album(title="Test Album", pageid=789, namespace=0)
        
        assert album.title == "Test Album"
        assert album.pageid == 789
        assert album.namespace == 0
    
    def test_rich_lyrics_dataclass(self):
        """Test RichLyrics dataclass"""
        lyrics = RichLyrics(
            title="Test Song",
            html_content="<b>Test Song</b> lyrics content",
            artist="Test Artist",
            album="Test Album",
            page_id=123
        )
        
        assert lyrics.title == "Test Song"
        assert lyrics.artist == "Test Artist"
        assert lyrics.album == "Test Album"
        assert lyrics.html_content == "<b>Test Song</b> lyrics content"
        assert lyrics.page_id == 123
