import pytest
from services.bhashini_service import BhashiniService

@pytest.fixture
def bhashini():
    # Setup in MOCK mode to bypass actual API calls during tests
    import os
    os.environ["BHASHINI_MOCK_MODE"] = "true"
    return BhashiniService()

@pytest.mark.asyncio
async def test_speech_to_text_mock(bhashini):
    # Test that in mock mode, it returns simulated text
    fake_audio_bytes = b"fakeaudio123"
    text = await bhashini.speech_to_text(fake_audio_bytes, source_lang="hi")
    
    assert isinstance(text, str)
    assert len(text) > 0

@pytest.mark.asyncio
async def test_translate_mock(bhashini):
    text = "नमस्ते, मेरा नाम अमित है।"
    
    # Vernacular to English
    translated = await bhashini.translate(text, source_lang="hi", target_lang="en")
    assert isinstance(translated, str)
    assert len(translated) > 0

    # English to Vernacular
    translated_back = await bhashini.translate("Hello, my name is Amit.", source_lang="en", target_lang="hi")
    assert isinstance(translated_back, str)
    assert len(translated_back) > 0

@pytest.mark.asyncio
async def test_text_to_speech_mock(bhashini):
    text = "आपका ऑर्डर कन्फर्म हो गया है।"
    audio_bytes = await bhashini.text_to_speech(text, target_lang="hi", gender="female")
    
    assert isinstance(audio_bytes, bytes)
    assert len(audio_bytes) > 0
