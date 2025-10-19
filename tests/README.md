# Mezmur Bot Test Suite

This directory contains comprehensive tests for the Mezmur Telegram Bot. The test suite is designed to ensure all functionality works correctly and to catch regressions when making changes.

## Test Structure

```
tests/
├── __init__.py                 # Test package initialization
├── conftest.py                 # Pytest fixtures and configuration
├── pytest.ini                 # Pytest configuration
├── requirements.txt            # Test dependencies
├── test_bot.py                 # Tests for main bot functionality
├── test_api_client.py          # Tests for API client
├── test_search_handler.py      # Tests for search handler
├── test_lyrics_handler.py      # Tests for lyrics handler
├── test_albums_handler.py      # Tests for albums handler
├── test_integration.py         # Integration tests
└── README.md                   # This file
```

## Test Categories

### 1. Unit Tests
- **test_bot.py**: Tests for the main MezmurBot class
  - Bot initialization
  - Command handlers (/start, /help)
  - Button callbacks
  - Text message handling
  - User state management
  - Health checks

- **test_api_client.py**: Tests for the MezmurAPIClient class
  - API endpoint calls
  - Data parsing and validation
  - Error handling
  - HTTP status codes

- **test_search_handler.py**: Tests for the SearchHandler class
  - Search commands (/search, /search_full)
  - Result formatting
  - Pagination
  - Callback handling

- **test_lyrics_handler.py**: Tests for the LyricsHandler class
  - Lyrics commands (/lyrics, /rich_lyrics, /random_lyrics)
  - Text formatting (plain and HTML)
  - Error handling

- **test_albums_handler.py**: Tests for the AlbumsHandler class
  - Album and artist commands
  - Keyboard creation
  - Callback handling

### 2. Integration Tests
- **test_integration.py**: End-to-end functionality tests
  - Complete user flows
  - Component interactions
  - Error propagation
  - State management

## Running Tests

### Prerequisites
Install test dependencies:
```bash
pip install -r tests/requirements.txt
```

### Quick Test Run
```bash
# Run all tests
python run_tests.py

# Run specific test types
python run_tests.py unit
python run_tests.py integration
python run_tests.py specific
```

### Manual Test Execution
```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_bot.py

# Run with verbose output
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html

# Run specific test
pytest tests/test_bot.py::TestMezmurBot::test_start_command
```

## Test Features

### Fixtures
The test suite includes comprehensive fixtures in `conftest.py`:
- **Mock API Client**: Simulates API responses
- **Mock Telegram Objects**: User, Message, Update, etc.
- **Sample Data**: Search results, artists, albums, lyrics
- **Test Context**: Properly configured test environment

### Mocking Strategy
- **API Calls**: All external API calls are mocked
- **Telegram API**: Telegram bot interactions are mocked
- **Async Operations**: Proper async/await testing
- **Error Scenarios**: Various error conditions are tested

### Test Coverage
The tests cover:
- ✅ All public methods and functions
- ✅ Success and error scenarios
- ✅ Edge cases and boundary conditions
- ✅ User interaction flows
- ✅ State management
- ✅ Data validation and formatting

## Writing New Tests

### Test Naming Convention
- Test files: `test_*.py`
- Test classes: `Test*`
- Test methods: `test_*`

### Example Test Structure
```python
class TestNewFeature:
    """Test cases for new feature"""
    
    def test_feature_initialization(self, mock_dependency):
        """Test feature initialization"""
        feature = NewFeature(mock_dependency)
        assert feature.dependency == mock_dependency
    
    @pytest.mark.asyncio
    async def test_async_feature(self, mock_update, mock_context):
        """Test async feature functionality"""
        feature = NewFeature(AsyncMock())
        await feature.async_method(mock_update, mock_context)
        
        # Assertions here
        mock_update.effective_message.reply_text.assert_called_once()
```

### Best Practices
1. **Use descriptive test names** that explain what is being tested
2. **Test one thing per test method**
3. **Use appropriate fixtures** from conftest.py
4. **Mock external dependencies** (APIs, Telegram, etc.)
5. **Test both success and failure scenarios**
6. **Use async/await properly** for async functions
7. **Assert specific behaviors**, not just that methods were called

## Continuous Integration

The test suite is designed to run in CI/CD environments:
- No external dependencies required
- All API calls are mocked
- Tests run quickly and reliably
- Clear pass/fail indicators

## Debugging Tests

### Running Individual Tests
```bash
# Run specific test with verbose output
pytest tests/test_bot.py::TestMezmurBot::test_start_command -v -s

# Run with debug output
pytest tests/test_bot.py -v -s --tb=long
```

### Common Issues
1. **Import Errors**: Ensure all dependencies are installed
2. **Async Issues**: Use `@pytest.mark.asyncio` for async tests
3. **Mock Issues**: Verify mocks are set up correctly
4. **Assertion Failures**: Check expected vs actual values

## Test Data

The test suite uses realistic sample data:
- **Search Results**: Actual song titles and metadata
- **Artists**: Real Ethiopian artist names
- **Albums**: Realistic album structures
- **Lyrics**: Sample lyrics content

This ensures tests are meaningful and catch real-world issues.

## Maintenance

### Adding New Features
1. Create tests for new functionality
2. Update existing tests if needed
3. Ensure all tests pass
4. Update this README if test structure changes

### Updating Tests
1. Run tests before making changes
2. Make changes incrementally
3. Run tests after each change
4. Fix any failing tests
5. Ensure test coverage remains high

## Performance

The test suite is optimized for speed:
- Parallel test execution where possible
- Minimal setup/teardown overhead
- Efficient mocking strategies
- Fast assertion methods

Typical test run time: < 30 seconds for full suite
