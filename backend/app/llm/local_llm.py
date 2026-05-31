import os
from typing import Optional


DEFAULT_LOCAL_LLM_MODEL = "llama3.2:3b"


def call_ollama(prompt: str, system: Optional[str] = None, model: Optional[str] = None) -> Optional[str]:
    """Call a local Ollama model and return text, or None when unavailable."""
    model_name = model or os.getenv("LOCAL_LLM_MODEL", DEFAULT_LOCAL_LLM_MODEL)
    try:
        import ollama
    except Exception:
        return None

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    try:
        response = ollama.chat(model=model_name, messages=messages)
    except Exception:
        return None

    message = response.get("message") if isinstance(response, dict) else None
    content = message.get("content") if isinstance(message, dict) else None
    return content.strip() if content else None

