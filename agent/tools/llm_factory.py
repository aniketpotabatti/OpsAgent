"""
LLM Factory for OpsAgent supporting OpenAI, Anthropic, and Gemini (Google).
"""

import os
from typing import Any

def get_llm(provider: str = None, api_key: str = None, model_name: str = None, temperature: float = 0.0) -> Any:
    """
    Instantiate and return a LangChain chat model based on provider.
    Supported providers: 'openai', 'anthropic', 'gemini' (or 'google').
    Falls back to environment variables if parameters are not explicitly passed.
    """
    selected_provider = (provider or os.getenv("LLM_PROVIDER") or "openai").lower()

    if selected_provider == "openai":
        key = api_key or os.getenv("OPENAI_API_KEY")
        if not key:
            raise ValueError("OPENAI_API_KEY is not set.")
        from langchain_openai import ChatOpenAI
        model = model_name or "gpt-3.5-turbo"
        return ChatOpenAI(openai_api_key=key, model_name=model, temperature=temperature)

    elif selected_provider in ["anthropic", "claude"]:
        key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not key:
            raise ValueError("ANTHROPIC_API_KEY is not set.")
        try:
            from langchain_anthropic import ChatAnthropic
        except ImportError:
            raise ImportError("langchain-anthropic package is required for Anthropic models. Install it via pip install langchain-anthropic.")
        model = model_name or "claude-3-haiku-20240307"
        return ChatAnthropic(anthropic_api_key=key, model_name=model, temperature=temperature)

    elif selected_provider in ["gemini", "google"]:
        key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not key:
            raise ValueError("GEMINI_API_KEY (or GOOGLE_API_KEY) is not set.")
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
        except ImportError:
            raise ImportError("langchain-google-genai package is required for Gemini models. Install it via pip install langchain-google-genai.")
        model = model_name or "gemini-1.5-flash"
        return ChatGoogleGenerativeAI(google_api_key=key, model=model, temperature=temperature)

    else:
        raise ValueError(f"Unsupported LLM provider: {selected_provider}. Choose from 'openai', 'anthropic', or 'gemini'.")
