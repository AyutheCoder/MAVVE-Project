import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
import sys

# Globally mock pydub to prevent audioop import error on Python 3.13 during test collection
sys.modules['pydub'] = MagicMock()
sys.modules['pydub.utils'] = MagicMock()
sys.modules['pydub.audio_segment'] = MagicMock()

@pytest.fixture
def mock_db_session():
    """Returns a mocked SQLAlchemy AsyncSession."""
    session = AsyncMock()
    return session

@pytest.fixture
def sample_order():
    """Realistic Indian sample order for testing."""
    return {
        "order_id": "ORD-TEST-001",
        "user_id": "usr_123",
        "total_amount": 499,
        "payment_mode": "COD",
        "delivery_address": {"raw": "missing landmark pune"},
        "pincode": "411001",
        "status": "PLACED"
    }

@pytest.fixture
def sample_user():
    """Realistic user profile for testing."""
    return {
        "user_id": "usr_123",
        "phone_number": "+919876543210",
        "name": "Amit Sharma",
        "preferred_language": "hi",
        "historical_rto_rate": 0.4
    }

@pytest.fixture(autouse=True)
def mock_llm_responses():
    """Globally mock LangChain ChatGoogleGenerativeAI to prevent real API calls during tests."""
    with patch('langchain_google_genai.ChatGoogleGenerativeAI.ainvoke', new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value.content = "This is a mocked LLM response."
        yield mock_llm
