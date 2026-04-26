"""LLM providers router returning available providers and models."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.schemas import LLMProviderSchema, LLMProvidersResponse
from app.services.settings import get_all_settings

router = APIRouter(prefix="/llm-providers", tags=["llm_providers"])

# Hardcoded provider definitions based on tradingagents config
PROVIDERS = [
    {
        "id": "openai",
        "name": "OpenAI",
        "models": [
            "gpt-5.2",
            "gpt-5-mini",
            "gpt-4.1",
            "gpt-4.1-mini",
            "gpt-4.1-nano",
            "o3",
            "o3-mini",
            "o4-mini",
        ],
        "requires_api_key": True,
    },
    {
        "id": "anthropic",
        "name": "Anthropic",
        "models": [
            "claude-sonnet-4-20250514",
            "claude-haiku-4-20250414",
            "claude-opus-4-20250514",
        ],
        "requires_api_key": True,
    },
    {
        "id": "google",
        "name": "Google",
        "models": [
            "gemini-2.5-pro",
            "gemini-2.5-flash",
            "gemini-2.0-flash",
            "gemini-2.0-flash-lite",
        ],
        "requires_api_key": True,
    },
    {
        "id": "xai",
        "name": "xAI",
        "models": [
            "grok-3",
            "grok-3-fast",
            "grok-3-mini",
            "grok-3-mini-fast",
        ],
        "requires_api_key": True,
    },
    {
        "id": "openrouter",
        "name": "OpenRouter",
        "models": [
            "openai/gpt-5.2",
            "anthropic/claude-sonnet-4-20250514",
            "google/gemini-2.5-pro",
            "deepseek/deepseek-r1",
            "deepseek/deepseek-chat-v3-0324",
            "meta-llama/llama-4-maverick",
        ],
        "requires_api_key": True,
    },
    {
        "id": "ollama",
        "name": "Ollama (Local)",
        "models": [
            "llama3.3",
            "llama3.2",
            "deepseek-r1",
            "qwen2.5",
            "gemma3",
            "phi4",
            "mistral",
        ],
        "requires_api_key": False,
    },
]


@router.get("", response_model=LLMProvidersResponse)
async def get_llm_providers(db: AsyncSession = Depends(get_db)):
    """Return available LLM providers with configuration status."""
    settings_data = await get_all_settings(db)
    api_keys = settings_data.get("api_keys", {})

    providers = []
    for p in PROVIDERS:
        is_configured = (
            not p["requires_api_key"] or api_keys.get(p["id"], False)
        )
        providers.append(
            LLMProviderSchema(
                id=p["id"],
                name=p["name"],
                models=p["models"],
                requires_api_key=p["requires_api_key"],
                is_configured=is_configured,
            )
        )

    return LLMProvidersResponse(providers=providers)
