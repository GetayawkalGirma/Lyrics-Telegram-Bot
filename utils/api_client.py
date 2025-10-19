"""
API Client for communicating with the Mezmur FastAPI service
"""
import httpx
from typing import List, Dict, Any, Optional
import asyncio
from dataclasses import dataclass


@dataclass
class SearchResult:
    title: str
    pageid: int
    snippet: Optional[str] = None
    size: Optional[int] = None
    wordcount: Optional[int] = None


@dataclass
class Artist:
    title: str
    pageid: int
    namespace: int


@dataclass
class Album:
    title: str
    pageid: int
    namespace: int


@dataclass
class Song:
    title: str
    pageid: int
    namespace: int
    artist: Optional[str] = None
    album: Optional[str] = None


@dataclass
class RichLyrics:
    title: str
    html_content: str
    artist: Optional[str] = None
    album: Optional[str] = None
    page_id: Optional[int] = None


@dataclass
class PaginatedResponse:
    data: List[Any]
    total: int
    page: int
    limit: int
    has_next: bool
    has_prev: bool
    next_token: Optional[str] = None


class MezmurAPIClient:
    """Client for interacting with the Mezmur FastAPI service"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
    
    async def health_check(self) -> Dict[str, Any]:
        """Check if the API is healthy"""
        try:
            response = await self.client.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise Exception(f"Health check failed: {str(e)}")
    
    # Search methods
    async def search_prefix(self, query: str, page: int = 1, limit: int = 10, continue_token: Any = None) -> PaginatedResponse:
        """Prefix search - fast search for titles starting with query"""
        params = {
            "q": query,
            "page": page,
            "limit": limit
        }
        if continue_token:
            params["continue_token"] = continue_token
        
        try:
            response = await self.client.get(f"{self.base_url}/search/prefix", params=params)
            response.raise_for_status()
            data = response.json()
            
            # Convert to SearchResult objects
            search_results = [
                SearchResult(
                    title=item["title"],
                    pageid=item["pageid"],
                    snippet=item.get("snippet"),
                    size=item.get("size"),
                    wordcount=item.get("wordcount")
                )
                for item in data["data"]
            ]
            
            return PaginatedResponse(
                data=search_results,
                total=data["total"],
                page=data["page"],
                limit=data["limit"],
                has_next=data["has_next"],
                has_prev=data["has_prev"],
                next_token=data.get("next_token")
            )
        except Exception as e:
            raise Exception(f"Prefix search failed: {str(e)}")
    
    async def search_full(self, query: str, page: int = 1, limit: int = 10, continue_token: Any = None) -> PaginatedResponse:
        """Full text search - searches anywhere in content"""
        params = {
            "q": query,
            "page": page,
            "limit": limit
        }
        if continue_token:
            params["continue_token"] = continue_token
        
        try:
            response = await self.client.get(f"{self.base_url}/search", params=params)
            response.raise_for_status()
            data = response.json()
            
            # Convert to SearchResult objects
            search_results = [
                SearchResult(
                    title=item["title"],
                    pageid=item["pageid"],
                    snippet=item.get("snippet"),
                    size=item.get("size"),
                    wordcount=item.get("wordcount")
                )
                for item in data["data"]
            ]
            
            return PaginatedResponse(
                data=search_results,
                total=data["total"],
                page=data["page"],
                limit=data["limit"],
                has_next=data["has_next"],
                has_prev=data["has_prev"],
                next_token=data.get("next_token")
            )
        except Exception as e:
            raise Exception(f"Full search failed: {str(e)}")
    
    # Artist methods
    async def get_artists(self, page: int = 1, limit: int = 20, continue_token: Any = None) -> PaginatedResponse:
        """Get all artists with pagination"""
        params = {
            "page": page,
            "limit": limit
        }
        if continue_token:
            params["continue_token"] = continue_token
        
        try:
            response = await self.client.get(f"{self.base_url}/artists", params=params)
            response.raise_for_status()
            data = response.json()
            
            # Convert to Artist objects
            artists = [
                Artist(
                    title=item["title"],
                    pageid=item["pageid"],
                    namespace=item["namespace"]
                )
                for item in data["data"]
            ]
            
            return PaginatedResponse(
                data=artists,
                total=data["total"],
                page=data["page"],
                limit=data["limit"],
                has_next=data["has_next"],
                has_prev=data["has_prev"],
                next_token=data.get("next_token")
            )
        except Exception as e:
            raise Exception(f"Get artists failed: {str(e)}")
    
    async def get_artist_albums(self, artist_name: str, page: int = 1, limit: int = 20, continue_token: Optional[Any] = None) -> PaginatedResponse:
        """Get albums by a specific artist"""
        params = {
            "page": page,
            "limit": limit
        }
        if continue_token:
            params["continue_token"] = continue_token
        
        try:
            response = await self.client.get(f"{self.base_url}/artists/{artist_name}/albums", params=params)
            response.raise_for_status()
            data = response.json()
            
            # Convert to Album objects
            albums = [
                Album(
                    title=item["title"],
                    pageid=item["pageid"],
                    namespace=item["namespace"]
                )
                for item in data["data"]
            ]
            
            return PaginatedResponse(
                data=albums,
                total=data["total"],
                page=data["page"],
                limit=data["limit"],
                has_next=data["has_next"],
                has_prev=data["has_prev"],
                next_token=data.get("next_token")
            )
        except Exception as e:
            raise Exception(f"Get artist albums failed: {str(e)}")
    
    # Album methods
    async def get_album_songs(self, album_title: str, page: int = 1, limit: int = 20) -> PaginatedResponse:
        """Get songs in a specific album"""
        params = {
            "album_title": album_title,
            "page": page,
            "limit": limit
        }
        
        try:
            response = await self.client.get(f"{self.base_url}/albums/songs", params=params)
            response.raise_for_status()
            data = response.json()
            
            # Convert to Song objects
            songs = [
                Song(
                    title=item["title"],
                    pageid=item["pageid"],
                    namespace=item["namespace"],
                    artist=item.get("artist"),
                    album=item.get("album")
                )
                for item in data["data"]
            ]
            
            return PaginatedResponse(
                data=songs,
                total=data["total"],
                page=data["page"],
                limit=data["limit"],
                has_next=data["has_next"],
                has_prev=data["has_prev"],
                next_token=data.get("next_token")
            )
        except Exception as e:
            raise Exception(f"Get album songs failed: {str(e)}")
    
    # Lyrics methods
    async def get_lyrics(self, song_title: str) -> Dict[str, Any]:
        """Get plain text lyrics for a song"""
        try:
            url = f"{self.base_url}/lyrics/{song_title}"
            print(f"Making request to: {url}")  # Debug print
            response = await self.client.get(url)
            print(f"Response status: {response.status_code}")  # Debug print
            print(f"Response text: {response.text[:200]}...")  # Debug print
            
            if response.status_code == 500:
                raise Exception(f"API server error (500) for song: {song_title}")
            
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise Exception(f"Get lyrics failed for '{song_title}': {str(e)}")
    
    async def get_rich_lyrics(self, song_title: str) -> RichLyrics:
        """Get rich HTML lyrics for a song"""
        try:
            response = await self.client.get(f"{self.base_url}/lyrics/rich/{song_title}")
            response.raise_for_status()
            data = response.json()
            
            return RichLyrics(
                title=data["title"],
                html_content=data["html_content"],
                artist=data.get("artist"),
                album=data.get("album"),
                page_id=data.get("page_id")
            )
        except Exception as e:
            raise Exception(f"Get rich lyrics failed: {str(e)}")
    
    # Utility methods
    def categorize_search_results(self, results: List[SearchResult]) -> Dict[str, List[SearchResult]]:
        """Categorize search results by type (artist, album, song)"""
        categorized = {
            "artists": [],
            "albums": [],
            "songs": []
        }
        
        for result in results:
            slash_count = result.title.count("/")
            if slash_count == 0:
                categorized["artists"].append(result)
            elif slash_count == 1:
                categorized["albums"].append(result)
            else:
                categorized["songs"].append(result)
        
        return categorized
    
    def format_search_results(self, results: List[SearchResult], max_results: int = 10) -> str:
        """Format search results for Telegram display"""
        if not results:
            return "No results found."
        
        formatted = []
        categorized = self.categorize_search_results(results[:max_results])
        
        if categorized["artists"]:
            formatted.append("👤 **ARTISTS**")
            for artist in categorized["artists"]:
                formatted.append(f"• {artist.title}")
            formatted.append("")
        
        if categorized["albums"]:
            formatted.append("💿 **ALBUMS**")
            for album in categorized["albums"]:
                album_name = album.title.split("/")[-1] if "/" in album.title else album.title
                formatted.append(f"• {album_name}")
            formatted.append("")
        
        if categorized["songs"]:
            formatted.append("🎵 **SONGS**")
            for song in categorized["songs"]:
                song_name = song.title.split("/")[-1] if "/" in song.title else song.title
                formatted.append(f"• {song_name}")
        
        return "\n".join(formatted)
