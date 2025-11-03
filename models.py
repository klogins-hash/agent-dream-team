"""Model configuration and creation."""

from strands.models.litellm import LiteLLMModel
import config


def create_model(temperature=None, max_tokens=None):
    """Create an OpenRouter model via LiteLLM.
    
    Args:
        temperature: Override default temperature
        max_tokens: Override default max tokens
        
    Returns:
        Configured LiteLLMModel instance
    """
    return LiteLLMModel(
        client_args={
            "api_base": config.OPENROUTER_API_BASE,
            "api_key": config.OPENROUTER_API_KEY,
            "custom_llm_provider": "openrouter",
        },
        model_id=f"openrouter/{config.MODEL_ID}",
        params={
            "temperature": temperature or config.TEMPERATURE,
            "max_tokens": max_tokens or config.MAX_TOKENS,
        }
    )
