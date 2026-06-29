"""
Centralized LLM factory for MAVVE.
Supports: Google Gemini (direct), OpenAI, and OpenRouter (OpenAI-compatible).
"""

from langchain_core.language_models.chat_models import BaseChatModel
from config import settings


def get_llm(temperature: float | None = None) -> BaseChatModel:
    """
    Returns the configured LLM instance based on settings.LLM_PROVIDER.
    
    Supported providers:
      - "gemini"     → Direct Google Gemini via langchain-google-genai
      - "openai"     → Direct OpenAI via langchain-openai
      - "openrouter" → Any model via OpenRouter (OpenAI-compatible API)
    """
    temp = temperature if temperature is not None else settings.LLM_TEMPERATURE

    if settings.LLM_PROVIDER == "openrouter":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=settings.LLM_MODEL_NAME,
            temperature=temp,
            openai_api_key=settings.OPENROUTER_API_KEY,
            openai_api_base="https://openrouter.ai/api/v1",
            default_headers={
                "HTTP-Referer": "https://mavve.app",
                "X-Title": "MAVVE",
            },
        )

    elif settings.LLM_PROVIDER == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=settings.LLM_MODEL_NAME,
            temperature=temp,
            openai_api_key=settings.OPENAI_API_KEY,
        )

    else:  # Default: gemini
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model=settings.LLM_MODEL_NAME,
            temperature=temp,
            google_api_key=settings.GOOGLE_API_KEY or "dummy_key",
        )
