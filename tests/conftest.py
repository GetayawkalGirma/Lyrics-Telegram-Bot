"""
Pytest configuration and fixtures for Mezmur Bot tests
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from telegram import Update, Message, User, Chat, CallbackQuery, InlineQuery
from telegram.ext import ContextTypes
from utils.api_client import MezmurAPIClient, SearchResult, Artist, Album, RichLyrics


@pytest.fixture
def mock_api_client():
    """Mock API client for testing"""
    client = AsyncMock(spec=MezmurAPIClient)
    return client


@pytest.fixture
def mock_search_results():
    """Mock search results for testing"""
    return [
        SearchResult(
            title="Samuel Tesfamichael/Misale Yeleleh/Yekebere",
            pageid=1,
            snippet="Beautiful Ethiopian song",
            size=1500,
            wordcount=200
        ),
        SearchResult(
            title="Samuel Tesfamichael/Misale Yeleleh/Misale Yeleleh",
            pageid=2,
            snippet="Another beautiful song",
            size=1200,
            wordcount=180
        )
    ]


@pytest.fixture
def mock_artists():
    """Mock artists for testing"""
    return [
        Artist(title="Samuel Tesfamichael", pageid=1, namespace=0),
        Artist(title="Getayawkal & Birucktawit", pageid=2, namespace=0),
        Artist(title="Tesfaye Chala", pageid=3, namespace=0)
    ]


@pytest.fixture
def mock_albums():
    """Mock albums for testing"""
    return [
        Album(title="Samuel Tesfamichael/Misale Yeleleh", pageid=1, namespace=0),
        Album(title="Getayawkal & Birucktawit/Enkuan Des Alachehu", pageid=2, namespace=0)
    ]


@pytest.fixture
def mock_lyrics_data():
    """Mock lyrics data for testing"""
    return {
        "title": "Yekebere",
        "artist": "Samuel Tesfamichael",
        "album": "Misale Yeleleh",
        "lyrics": "Yekebere yekebere...\nBeautiful lyrics here..."
    }


@pytest.fixture
def mock_user():
    """Mock Telegram user for testing"""
    return User(
        id=12345,
        is_bot=False,
        first_name="Test",
        last_name="User",
        username="testuser"
    )


@pytest.fixture
def mock_chat():
    """Mock Telegram chat for testing"""
    return Chat(
        id=12345,
        type="private"
    )


@pytest.fixture
def mock_message(mock_user, mock_chat):
    """Mock Telegram message for testing"""
    message = MagicMock(spec=Message)
    message.from_user = mock_user
    message.chat = mock_chat
    message.text = "test message"
    message.reply_text = AsyncMock()
    return message


@pytest.fixture
def mock_update(mock_message):
    """Mock Telegram update for testing"""
    update = MagicMock(spec=Update)
    update.effective_message = mock_message
    update.effective_user = mock_message.from_user
    update.callback_query = None
    update.inline_query = None
    return update


@pytest.fixture
def mock_callback_query(mock_user, mock_message):
    """Mock Telegram callback query for testing"""
    query = MagicMock(spec=CallbackQuery)
    query.from_user = mock_user
    query.message = mock_message
    query.data = "test_callback"
    query.answer = AsyncMock()
    return query


@pytest.fixture
def mock_inline_query(mock_user):
    """Mock Telegram inline query for testing"""
    query = MagicMock(spec=InlineQuery)
    query.from_user = mock_user
    query.query = "test query"
    query.offset = "0"
    query.answer = AsyncMock()
    return query


@pytest.fixture
def mock_context():
    """Mock Telegram context for testing"""
    context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
    context.args = []
    return context


@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_application():
    """Mock Telegram application for testing"""
    app = AsyncMock()
    app.bot = AsyncMock()
    app.bot.set_my_commands = AsyncMock()
    app.initialize = AsyncMock()
    app.start = AsyncMock()
    app.stop = AsyncMock()
    app.shutdown = AsyncMock()
    app.updater = AsyncMock()
    app.updater.start_polling = AsyncMock()
    app.updater.stop = AsyncMock()
    return app
